from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.routes import router
from app.core.config import get_settings
from app.db.client import SupabaseDataClient
from app.db.repository import SupabaseRepository
from app.repository import InMemoryRepository, Repository
from app.services.chat import ChatService
from app.services.llm import LlmOrchestrator
from app.services.tools import ToolEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    repository: Repository
    if settings.data_repository == "local":
        repository = InMemoryRepository()
    else:
        if not settings.supabase_configured:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY are required")
        repository = SupabaseRepository(
            SupabaseDataClient(settings.supabase_data_api_url, settings.supabase_secret_key)
        )
    tools = ToolEngine(repository)
    llm = LlmOrchestrator(settings, tools)
    app.state.settings = settings
    app.state.repository = repository
    app.state.tools = tools
    app.state.llm = llm
    app.state.chat_service = ChatService(repository, tools, llm)
    try:
        yield
    finally:
        close = getattr(repository, "close", None)
        if close:
            await close()


app = FastAPI(
    title="Sadaqah Intelligence API",
    version="0.2.0",
    description="Source-linked humanitarian information with grounded LLM responses.",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
