import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import ContextAssistant from "../components/ContextAssistant";
import ProductNav from "../components/ProductNav";
import { api } from "../lib/api";
import type { Ngo, RegionStat } from "../lib/types";

const metricRows: Array<{ label: string; value: (ngo: Ngo) => string }> = [
  { label: "Founded", value: (ngo) => String(ngo.foundedYear) },
  { label: "Years operating", value: (ngo) => `${ngo.yearsActive} years` },
  { label: "Latest report", value: (ngo) => String(ngo.reportingYear) },
  { label: "Reported reach", value: (ngo) => ngo.reportedReach },
  { label: "Countries active", value: (ngo) => String(ngo.countriesActive) },
  { label: "Annual income", value: (ngo) => ngo.annualIncome ?? "Not available" },
  { label: "Annual expenditure", value: (ngo) => ngo.annualExpenditure ?? "Not available" },
  { label: "Reported activity", value: (ngo) => ngo.reportedActivity ?? "Not available" },
];

const isReadableSource = (url: string) => !url.includes("api.hpc.tools") && !url.includes("api.unhcr.org");

export default function ComparePage() {
  const crisisId = new URLSearchParams(window.location.search).get("crisis") ?? "";
  const [crisis, setCrisis] = useState<RegionStat | null>(null);
  const [ngoProfiles, setNgoProfiles] = useState<Ngo[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [selected, setSelected] = useState<Ngo[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!crisisId) return;
    Promise.all([api.crisis(crisisId), api.crisisNgos(crisisId)])
      .then(([crisisProfile, documented]) => {
        const initial = documented.slice(0, 3);
        setCrisis(crisisProfile);
        setNgoProfiles(documented);
        setSelectedIds(initial.map((ngo) => ngo.id));
      })
      .catch(() => setError(true));
  }, [crisisId]);

  useEffect(() => {
    if (selectedIds.length < 2 || !crisisId) {
      setSelected([]);
      return;
    }
    api.compare(selectedIds, crisisId)
      .then((response) => setSelected(response.organizations))
      .catch(() => setError(true));
  }, [crisisId, selectedIds]);

  const toggleNgo = (id: string) => {
    setSelectedIds((current) => {
      if (current.includes(id)) return current.length > 2 ? current.filter((item) => item !== id) : current;
      return current.length < 3 ? [...current, id] : [...current.slice(1), id];
    });
  };

  return (
    <div className="product-page compare-page">
      <ProductNav active="compare" />
      <main className="compare-main">
        <motion.header className="product-heading compare-heading" initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }}>
          <div><p className="page-kicker"><i /> {crisis?.name ?? "Selected crisis"} responders</p><h1>Compare organizations.<br /><em>In this response.</em></h1></div>
          <p>Select two or three organizations documented in {crisis?.name ?? "this crisis"}. Compare their published reach, coverage, activity, and reports.</p>
        </motion.header>

        <a className="compare-back-link" href={`/globe?crisis=${crisisId}`}><span aria-hidden="true">{"<-"}</span> Back to {crisis?.name ?? "crisis globe"}</a>

        {error && <div className="api-error page-error"><strong>Comparison unavailable</strong><span>Return to the globe and select a crisis location again.</span></div>}

        {!error && crisis && (
          <>
            <section className="compare-toolbar factual-toolbar">
              <div><span>Organization comparison</span><strong>Latest published information</strong></div>
              <p><b>{selectedIds.length}</b> organizations selected</p>
            </section>

            <section className="ngo-picker">
              {ngoProfiles.map((ngo) => {
                const isSelected = selectedIds.includes(ngo.id);
                return <button className={isSelected ? "active" : ""} onClick={() => toggleNgo(ngo.id)} type="button" key={ngo.id}><span style={{ background: ngo.accent }}>{ngo.initials}</span><div><strong>{ngo.name}</strong><small>Documented in {crisis.name}</small></div><i>{isSelected ? "Selected" : "Add"}</i></button>;
              })}
            </section>

            {ngoProfiles.length < 2 && <div className="api-error page-error"><strong>More evidence needed</strong><span>Fewer than two organizations currently have documented activity for this crisis.</span></div>}

            <motion.section className="comparison-cards" layout>
              {selected.map((ngo) => (
                <motion.article className="ngo-card objective-card" layout key={ngo.id} initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} whileHover={{ y: -8 }} transition={{ type: "spring", stiffness: 190, damping: 22 }}>
                  <div className="ngo-card-head"><span style={{ background: ngo.accent }}>{ngo.initials}</span><div><small>{ngo.descriptor}</small><h2>{ngo.name}</h2></div></div>
                  <div className="ngo-score objective-value"><strong>{ngo.reportedReach}</strong><span><b>Reported reach</b><small>{ngo.reportingYear} reporting period</small></span></div>
                  <div className="ngo-meta">
                    <span>Founded<strong>{ngo.foundedYear} ({ngo.yearsActive} years)</strong></span>
                    <span>Countries active<strong>{ngo.countriesActive}</strong></span>
                    <span>Coverage<strong>{ngo.coverage}</strong></span>
                    <span>Reported activity<strong>{ngo.reportedActivity ?? "See annual report"}</strong></span>
                  </div>
                  <div className="verified-list">{ngo.focusAreas.map((item) => <span key={item}><i />{item}</span>)}</div>
                  <button aria-expanded={expandedId === ngo.id} onClick={() => setExpandedId((current) => current === ngo.id ? null : ngo.id)} type="button">{expandedId === ngo.id ? "Hide evidence profile" : "View evidence profile"} <span aria-hidden="true">{expandedId === ngo.id ? "-" : "+"}</span></button>
                  {expandedId === ngo.id && (
                    <div className="card-breakdown fact-breakdown">
                      <div><span>Annual income<small>Latest report</small></span><b>{ngo.annualIncome ?? "Not available"}</b></div>
                      <div><span>Annual expenditure<small>Latest report</small></span><b>{ngo.annualExpenditure ?? "Not available"}</b></div>
                      <div><span>Giving types<small>Published donation options</small></span><b>{ngo.acceptedGivingTypes.join(", ")}</b></div>
                      <p>Official sources <strong>{ngo.sources.filter((source) => isReadableSource(source.url)).length}</strong></p>
                      {ngo.sources.filter((source) => isReadableSource(source.url)).map((source) => <a className="evidence-source-link" href={source.url} target="_blank" rel="noreferrer" key={source.url}><span>{source.title}<small>{source.sourceType}</small></span><b>{source.reportingYear ?? "Open"}</b></a>)}
                    </div>
                  )}
                  <a className="ngo-donation-link" href={ngo.donationUrl} target="_blank" rel="noreferrer">Visit official donation page <span aria-hidden="true">{"->"}</span></a>
                </motion.article>
              ))}
            </motion.section>

            {selected.length > 0 && (
              <section className="comparison-matrix">
                <header><div><p>Organization details</p><h2>Compare their latest published figures</h2></div><span>Reporting periods are shown for context</span></header>
                <div className="matrix-table objective-matrix">
                  <div className="matrix-row matrix-head"><span>Reported metric</span>{selected.map((ngo) => <strong key={ngo.id}>{ngo.shortName}</strong>)}</div>
                  {metricRows.map((metric) => <div className="matrix-row text-row" key={metric.label}><span>{metric.label}</span>{selected.map((ngo) => <strong className="matrix-fact" data-ngo={ngo.shortName} key={ngo.id}>{metric.value(ngo)}</strong>)}</div>)}
                  <div className="matrix-row text-row"><span>Accepted giving types</span>{selected.map((ngo) => <strong className="matrix-fact" data-ngo={ngo.shortName} key={ngo.id}>{ngo.acceptedGivingTypes.join(", ")}</strong>)}</div>
                </div>
              </section>
            )}

            {selected.length >= 2 && <ContextAssistant title="Ask about this comparison" subtitle="Ask about the selected organizations and their reports." contextType="ngo_comparison" crisisId={crisisId} ngoIds={selected.map((ngo) => ngo.id)} prompts={["Explain the differences between the selected NGOs", "What reporting periods are shown?", "Show the official sources"]} />}
          </>
        )}
      </main>
    </div>
  );
}
