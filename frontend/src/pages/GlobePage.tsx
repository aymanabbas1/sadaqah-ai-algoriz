import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import Globe, { GlobeMethods } from "react-globe.gl";
import { MeshPhongMaterial } from "three";
import ContextAssistant from "../components/ContextAssistant";
import ProductNav from "../components/ProductNav";
import { api } from "../lib/api";
import type { RegionStat } from "../lib/types";

type CountryFeature = {
  properties: Record<string, string | number>;
  geometry: { type: string; coordinates: unknown };
};

type GlobeSummary = {
  crisisProfiles: number;
  countriesCovered: number;
  sourceRecords: number;
};

const markerColor = "#71ddc0";
const getCountryName = (feature: CountryFeature) => String(feature.properties.ADMIN ?? feature.properties.NAME ?? "Unknown");
const isReadableSource = (url: string) => !url.includes("api.hpc.tools") && !url.includes("api.unhcr.org");

export default function GlobePage() {
  const globeRef = useRef<GlobeMethods | undefined>(undefined);
  const stageRef = useRef<HTMLDivElement>(null);
  const materialRef = useRef(new MeshPhongMaterial({ color: "#092c37", emissive: "#031014", shininess: 12, transparent: true, opacity: 0.98 }));
  const [countries, setCountries] = useState<CountryFeature[]>([]);
  const [regions, setRegions] = useState<RegionStat[]>([]);
  const [summary, setSummary] = useState<GlobeSummary | null>(null);
  const [selected, setSelected] = useState<RegionStat | null>(null);
  const [selectedCountry, setSelectedCountry] = useState("");
  const [error, setError] = useState(false);
  const [size, setSize] = useState({ width: 780, height: 650 });
  const [isMobile, setIsMobile] = useState(() => window.matchMedia("(max-width: 700px)").matches);
  const [globeInteractive, setGlobeInteractive] = useState(() => !window.matchMedia("(max-width: 700px)").matches);

  useEffect(() => {
    const media = window.matchMedia("(max-width: 700px)");
    const syncViewport = () => {
      setIsMobile(media.matches);
      setGlobeInteractive(!media.matches);
    };
    syncViewport();
    media.addEventListener("change", syncViewport);
    return () => media.removeEventListener("change", syncViewport);
  }, []);

  useEffect(() => {
    Promise.all([
      api.globe(),
      fetch("/data/countries.geojson").then((response) => response.json() as Promise<{ features: CountryFeature[] }>),
    ])
      .then(([payload, geoData]) => {
        const requestedId = new URLSearchParams(window.location.search).get("crisis");
        const initial = payload.regions.find((region) => region.id === requestedId) ?? payload.regions[0] ?? null;
        setRegions(payload.regions);
        setSummary(payload.summary);
        setCountries(geoData.features);
        setSelected(initial);
        setSelectedCountry(initial?.country ?? "");
      })
      .catch(() => setError(true));
  }, []);

  useEffect(() => {
    if (!stageRef.current) return;
    const updateSize = () => {
      if (!stageRef.current) return;
      const width = Math.max(280, stageRef.current.getBoundingClientRect().width);
      const viewportHeight = window.visualViewport?.height ?? window.innerHeight;
      const height = isMobile
        ? Math.max(320, Math.min(420, viewportHeight * 0.42))
        : Math.max(500, Math.min(700, width * 0.82));
      setSize({ width, height });
    };
    const observer = new ResizeObserver(updateSize);
    observer.observe(stageRef.current);
    window.addEventListener("resize", updateSize);
    updateSize();
    return () => {
      observer.disconnect();
      window.removeEventListener("resize", updateSize);
    };
  }, [isMobile]);

  useEffect(() => {
    const controls = globeRef.current?.controls();
    if (controls) {
      controls.enabled = !isMobile || globeInteractive;
      controls.autoRotate = !isMobile;
    }
    globeRef.current?.renderer().setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.25 : 2));
  }, [globeInteractive, isMobile]);

  useEffect(() => {
    if (!selected || !globeRef.current) return;
    globeRef.current.pointOfView({ lat: selected.lat, lng: selected.lng, altitude: isMobile ? 1.9 : 1.55 }, 450);
  }, [isMobile, selected, size.width]);

  const selectRegion = (region: RegionStat) => {
    setSelected(region);
    setSelectedCountry(region.country);
  };

  const onReady = () => {
    const controls = globeRef.current?.controls();
    if (controls) {
      controls.autoRotate = !isMobile;
      controls.autoRotateSpeed = 0.28;
      controls.enableDamping = true;
      controls.dampingFactor = 0.08;
      controls.enabled = !isMobile || globeInteractive;
    }
    globeRef.current?.renderer().setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.25 : 2));
    globeRef.current?.pointOfView({ lat: selected?.lat ?? 17, lng: selected?.lng ?? 36, altitude: isMobile ? 1.9 : 1.9 }, 0);
  };

  const polygonColor = (item: object) => {
    const name = getCountryName(item as CountryFeature);
    if (name === selectedCountry) return "rgba(105, 232, 196, 0.82)";
    if (regions.some((entry) => entry.country === name)) return "rgba(73, 161, 151, 0.52)";
    return "rgba(35, 88, 98, 0.34)";
  };

  const visibleSources = selected?.sources.filter((source) => isReadableSource(source.url)) ?? [];
  const selectedIndex = selected ? regions.findIndex((region) => region.id === selected.id) : 0;

  const slideCrisis = (direction: -1 | 1) => {
    if (!regions.length) return;
    const nextIndex = (selectedIndex + direction + regions.length) % regions.length;
    selectRegion(regions[nextIndex]);
  };

  return (
    <div className="product-page globe-page">
      <ProductNav active="globe" />
      <main className="globe-main">
        <motion.header className="product-heading globe-heading" initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }}>
          <div><p className="page-kicker"><i /> Global humanitarian view</p><h1>Explore crises.<br /><em>Keep the context.</em></h1></div>
          <p>Select a crisis location to understand the situation, review official sources, and compare documented responders.</p>
        </motion.header>

        {error && <div className="api-error page-error"><strong>Backend unavailable</strong><span>Start the FastAPI service, then reload this page.</span></div>}
        {!error && (!selected || !summary) && <div className="api-loading">Loading sourced crisis profiles...</div>}

        {!error && selected && summary && (
          <>
            <section className="globe-summary">
              <div><span>Crisis profiles</span><strong>{String(summary.crisisProfiles).padStart(2, "0")}</strong><small>Explore by location</small></div>
              <div><span>Countries covered</span><strong>{String(summary.countriesCovered).padStart(2, "0")}</strong><small>Across active response plans</small></div>
              <div><span>Sources</span><strong>{summary.sourceRecords}</strong><small>Official pages and reports</small></div>
            </section>

            <section className="globe-workspace">
              <aside className="globe-controls crisis-index">
                <div><p>Crisis index</p><small>Select a location to open its profile.</small></div>
                <div className="region-queue">
                  {regions.map((region) => <button className={selected.id === region.id ? "active" : ""} onClick={() => selectRegion(region)} type="button" key={region.id}><span><i style={{ background: markerColor }} />{region.name}<small>{region.crisisType}</small></span></button>)}
                </div>
                <div className="mobile-crisis-slider" aria-label="Select a crisis location">
                  <button aria-label="Previous crisis" onClick={() => slideCrisis(-1)} type="button"><span aria-hidden="true">{"<-"}</span></button>
                  <motion.div key={selected.id} initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }}>
                    <small>Crisis location {selectedIndex + 1} of {regions.length}</small>
                    <strong>{selected.name}</strong>
                    <span>{selected.crisisType}</span>
                  </motion.div>
                  <button aria-label="Next crisis" onClick={() => slideCrisis(1)} type="button"><span aria-hidden="true">{"->"}</span></button>
                </div>
              </aside>

              <div className={`globe-stage ${globeInteractive ? "touch-active" : ""}`} ref={stageRef}>
                <div className="globe-stage-label"><span><i /> Drag to explore</span><span>Scroll to zoom</span></div>
                {isMobile && !globeInteractive && <div className="globe-touch-gate"><button onClick={() => setGlobeInteractive(true)} type="button"><span>Explore globe</span><small>Tap to enable drag and zoom</small></button></div>}
                {isMobile && globeInteractive && <button className="globe-touch-done" onClick={() => setGlobeInteractive(false)} type="button">Done</button>}
                <Globe
                  ref={globeRef}
                  width={size.width}
                  height={size.height}
                  backgroundColor="rgba(0,0,0,0)"
                  rendererConfig={{ antialias: !isMobile, alpha: true, powerPreference: "high-performance" }}
                  globeMaterial={materialRef.current}
                  showAtmosphere
                  atmosphereColor="#65d9c0"
                  atmosphereAltitude={0.18}
                  showGraticules={!isMobile}
                  polygonsData={countries}
                  polygonCapColor={polygonColor}
                  polygonSideColor={() => "rgba(3,18,24,0.5)"}
                  polygonStrokeColor={() => "rgba(151,220,211,0.2)"}
                  polygonAltitude={(item: object) => getCountryName(item as CountryFeature) === selectedCountry ? 0.025 : 0.009}
                  polygonsTransitionDuration={isMobile ? 0 : 350}
                  polygonLabel={(item: object) => `<div class="globe-tooltip"><strong>${getCountryName(item as CountryFeature)}</strong><span>Select a profile marker</span></div>`}
                  onPolygonClick={(item: object) => {
                    const name = getCountryName(item as CountryFeature);
                    const region = regions.find((entry) => entry.country === name);
                    if (region) selectRegion(region);
                  }}
                  pointsData={regions}
                  pointLat="lat"
                  pointLng="lng"
                  pointColor={() => markerColor}
                  pointAltitude={0.075}
                  pointRadius={0.19}
                  pointResolution={isMobile ? 8 : 16}
                  pointLabel={(item: object) => { const region = item as RegionStat; return `<div class="globe-tooltip"><small>${region.crisisType}</small><strong>${region.name}</strong><span>Open sourced profile</span></div>`; }}
                  onPointClick={(item: object) => selectRegion(item as RegionStat)}
                  ringsData={[selected]}
                  ringLat="lat"
                  ringLng="lng"
                  ringColor={() => [markerColor, "rgba(255,255,255,0)"]}
                  ringMaxRadius={3.2}
                  ringPropagationSpeed={1.3}
                  ringRepeatPeriod={1400}
                  onGlobeReady={onReady}
                />
                <div className="globe-legend"><span><i style={{ background: markerColor }} />Crisis profile</span><span><i style={{ background: "#eafff8" }} />Selected pulse</span></div>
              </div>

              <motion.aside className="region-detail crisis-profile" key={selected.id} initial={{ opacity: 0, x: 18 }} animate={{ opacity: 1, x: 0 }}>
                <div className="region-detail-top"><span>Official sources</span><b>{visibleSources.length} {visibleSources.length === 1 ? "reference" : "references"}</b></div>
                <h2>{selected.name}</h2><p>{selected.summary}</p>
                <div className="detail-grid crisis-facts">
                  <span>People in need<strong>{selected.peopleInNeed}</strong></span>
                  <span>Displacement<strong>{selected.displacedPeople}</strong></span>
                  <span>Funding context<strong>{selected.fundingStatus}</strong></span>
                  <span>Crisis type<strong>{selected.crisisType}</strong></span>
                </div>
                <div className="detail-tags"><p>Focus areas</p><div>{selected.focusAreas.map((item) => <span key={item}>{item}</span>)}</div></div>
                <div className="detail-tags"><p>Affected locations</p><div>{selected.affectedLocations.map((item) => <span key={item}>{item}</span>)}</div></div>
                {visibleSources.length > 0 && <div className="detail-sources"><p>Official sources</p>{visibleSources.map((source) => <a href={source.url} target="_blank" rel="noreferrer" key={source.url}><span>{source.organization}</span><strong>{source.title}</strong><small>{source.reportingYear ?? "Current page"} - Read official update</small></a>)}</div>}
                <a href={`/compare?crisis=${selected.id}`}>See NGOs responding here <span aria-hidden="true">{"->"}</span></a>
              </motion.aside>
            </section>

            <ContextAssistant
              title={`Ask about ${selected.name}`}
              subtitle="Ask for a summary, responding organizations, or source links."
              contextType="crisis"
              crisisId={selected.id}
              prompts={["Summarize this crisis", "Which organizations have documented activity here?", "Show the official sources"]}
            />
          </>
        )}
      </main>
    </div>
  );
}
