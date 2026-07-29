export type ProductPage = "globe" | "compare";

const links: Array<{ id: ProductPage; label: string; path: string }> = [
  { id: "globe", label: "Crisis globe", path: "/globe" },
];

export default function ProductNav({ active }: { active: ProductPage }) {
  return (
    <nav className="product-nav">
      <a className="product-brand" href="/"><span>SI</span><strong>Sadaqah Intelligence</strong></a>
      <div className="product-nav-links" aria-label="Product navigation">
        {links.map((link) => <a className={active === link.id ? "active" : ""} href={link.path} key={link.id}>{link.label}</a>)}
      </div>
      <a className="product-nav-action" href="/globe">Explore crises</a>
    </nav>
  );
}
