import os

from fastapi.testclient import TestClient

os.environ["DATA_REPOSITORY"] = "local"

from app.main import app


def test_health_reports_local_repository() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["repository"] == "local"


def test_globe_is_alphabetical_and_has_no_ranking_fields() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/globe")
        assert response.status_code == 200
        body = response.json()
        names = [region["name"] for region in body["regions"]]
        assert names == sorted(names)
        assert body["summary"]["crisisProfiles"] == 8
        assert "arcs" not in body
        for region in body["regions"]:
            assert "needIndex" not in region
            assert "priorityBreakdown" not in region
            assert region["sources"]


def test_crisis_profile_and_documented_ngos_have_sources() -> None:
    with TestClient(app) as client:
        crisis = client.get("/api/v1/crises/sudan")
        responders = client.get("/api/v1/crises/sudan/ngos")
        assert crisis.status_code == 200
        assert all(source["url"].startswith("https://") for source in crisis.json()["sources"])
        assert responders.status_code == 200
        assert len(responders.json()) >= 2
        assert all("sudan" in ngo["crisisIds"] and ngo["sources"] for ngo in responders.json())
        assert all(ngo["donationUrl"].startswith("https://") for ngo in responders.json())


def test_compare_preserves_selection_order_without_a_winner() -> None:
    ids = ["islamic-relief", "care", "mercy-corps"]
    with TestClient(app) as client:
        response = client.post("/api/v1/ngos/compare", json={"ids": ids, "crisisId": "sudan"})
        assert response.status_code == 200
        body = response.json()
        assert [ngo["id"] for ngo in body["organizations"]] == ids
        assert "winner" not in body
        assert "score" not in body
        assert "documented in Sudan" in body["rationale"]


def test_compare_rejects_an_ngo_not_documented_in_the_selected_crisis() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/ngos/compare",
            json={"ids": ["human-appeal", "care"], "crisisId": "drc"},
        )
        assert response.status_code == 422


def test_ranking_request_is_refused_and_returns_no_recommendation() -> None:
    with TestClient(app) as client:
        client.app.state.llm.client = None
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Which is the best NGO?",
                "contextType": "ngo_comparison",
                "crisisId": "sudan",
                "ngoIds": ["care", "mercy-corps"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert "do not rank" in body["message"].lower()
        assert "recommendation" not in body
        assert body["intent"] == "compare_ngos"


def test_contextual_crisis_chat_returns_profile_sources() -> None:
    with TestClient(app) as client:
        client.app.state.llm.client = None
        response = client.post(
            "/api/v1/chat",
            json={"message": "Summarize this crisis", "contextType": "crisis", "crisisId": "sudan"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["intent"] == "crisis_lookup"
        assert body["sources"]
        assert body["artifacts"][0]["type"] == "crisis_profile"


def test_ngo_screen_context_forces_selected_ngo_comparison() -> None:
    with TestClient(app) as client:
        client.app.state.llm.client = None
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Explain the differences between the selected NGOs",
                "contextType": "ngo_comparison",
                "crisisId": "sudan",
                "ngoIds": ["care", "mercy-corps"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["intent"] == "compare_ngos"
        assert body["artifacts"][0]["type"] == "ngo_comparison"
        assert {source["organization"] for source in body["sources"]} <= {"CARE", "Mercy Corps"}


def test_crisis_screen_source_request_returns_only_crisis_sources() -> None:
    with TestClient(app) as client:
        client.app.state.llm.client = None
        response = client.post(
            "/api/v1/chat",
            json={"message": "Show the official sources", "contextType": "crisis", "crisisId": "sudan"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["intent"] == "sources"
        assert body["artifacts"][0]["type"] == "sources"
        assert {source["organization"] for source in body["sources"]} == {"UNHCR", "OCHA ReliefWeb"}


def test_methodology_exposes_tools_and_no_score_models() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/methodology")
        assert response.status_code == 200
        body = response.json()
        assert len(body["tools"]) == 7
        assert len(body["ngoMetrics"]) == 7
        assert "scoreModels" not in body
        assert any("never ranked" in principle for principle in body["principles"])
