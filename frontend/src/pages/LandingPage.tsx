import { motion } from "framer-motion";

const signals = [
  { label: "West Africa", className: "horizon-signal signal-west" },
  { label: "Horn of Africa", className: "horizon-signal signal-horn" },
  { label: "South Asia", className: "horizon-signal signal-asia" },
];

export default function LandingPage() {
  return (
    <main className="horizon-landing">
      <section className="horizon-hero">
        <nav className="horizon-nav">
          <a className="horizon-brand" href="/">
            <span className="horizon-brand-mark">SI</span>
            <span>Sadaqah Intelligence</span>
          </a>
          <div className="horizon-nav-links">
            <a href="/globe">Crisis globe</a>
          </div>
          <a className="horizon-nav-cta" href="/globe">
            Open globe <span aria-hidden="true">{"->"}</span>
          </a>
        </nav>

        <motion.img
          className="earth-horizon"
          src="/assets/earth-horizon.png"
          alt=""
          initial={{ scale: 1.035, opacity: 0 }}
          animate={{ scale: [1.035, 1.055, 1.035], x: [0, -8, 0], opacity: 1 }}
          transition={{ opacity: { duration: 1.2 }, scale: { duration: 16, repeat: Infinity, ease: "easeInOut" }, x: { duration: 16, repeat: Infinity, ease: "easeInOut" } }}
        />
        <div className="horizon-vignette" aria-hidden="true" />
        <motion.div className="horizon-orbit orbit-one" aria-hidden="true" animate={{ rotate: 360 }} transition={{ duration: 70, repeat: Infinity, ease: "linear" }} />
        <motion.div className="horizon-orbit orbit-two" aria-hidden="true" animate={{ rotate: -360 }} transition={{ duration: 92, repeat: Infinity, ease: "linear" }} />

        {signals.map((signal, index) => (
          <motion.div className={signal.className} key={signal.label} initial={{ opacity: 0, scale: 0.7 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 1.05 + index * 0.18, duration: 0.6 }}>
            <motion.span animate={{ scale: [1, 1.8, 1], opacity: [0.9, 0.15, 0.9] }} transition={{ duration: 2.6 + index * 0.4, repeat: Infinity }} />
            <small>{signal.label}</small>
          </motion.div>
        ))}

        <motion.div className="horizon-copy" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.9, ease: "easeOut" }}>
          <p className="horizon-eyebrow"><span /> Humanitarian intelligence, made visible</p>
          <h1>See each crisis <em>in context.</em></h1>
          <p className="horizon-subtitle">Explore humanitarian crises, see which organizations are responding, and open the sources behind the information.</p>
          <div className="horizon-actions">
            <a className="horizon-primary" href="/globe">Explore the globe <span aria-hidden="true">{"->"}</span></a>
          </div>
        </motion.div>

        <div className="horizon-source-note">
          <span className="source-pulse" />
          <span>Official humanitarian data</span>
          <span>NGO reports</span>
          <span>Daily source checks</span>
        </div>
      </section>
    </main>
  );
}
