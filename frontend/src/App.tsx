import { lazy, Suspense, useEffect } from "react";
import LandingPage from "./pages/LandingPage";

const ComparePage = lazy(() => import("./pages/ComparePage"));
const GlobePage = lazy(() => import("./pages/GlobePage"));

function RedirectToGlobe() {
  useEffect(() => {
    window.location.replace("/globe");
  }, []);

  return <div className="page-loader"><span>SI</span><p>Selecting a crisis location...</p></div>;
}

export default function App() {
  const path = window.location.pathname.replace(/\/$/, "") || "/";

  const page = path === "/globe" || path === "/assistant"
      ? <GlobePage />
      : path === "/compare"
        ? new URLSearchParams(window.location.search).has("crisis") ? <ComparePage /> : <RedirectToGlobe />
        : null;

  if (page) {
    return <Suspense fallback={<div className="page-loader"><span>SI</span><p>Loading sourced profiles...</p></div>}>{page}</Suspense>;
  }

  return <LandingPage />;
}
