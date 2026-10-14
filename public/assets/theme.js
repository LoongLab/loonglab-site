// Applies the saved or system theme before first paint, and keeps the browser
// theme-color in sync. Blocking head script so there is no flash on navigation.
(() => {
  const root = document.documentElement;
  const key = "loonglab-theme";
  const system = window.matchMedia("(prefers-color-scheme: dark)");
  const parse = (v) => (v === "light" || v === "dark" ? v : null);

  let choice = null;
  try {
    choice = parse(window.localStorage.getItem(key));
  } catch {
    // Storage may be unavailable; the toggle still works for this page view.
  }

  const apply = () => {
    const theme = choice ?? (system.matches ? "dark" : "light");
    root.setAttribute("data-theme", theme);
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "dark" ? "#1e1e2e" : "#ffffff");
  };

  apply();
  system.addEventListener("change", () => {
    if (choice === null) apply();
  });
})();
