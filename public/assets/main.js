// Progressive enhancement: theme toggle, dynamic year, and copy buttons.
(() => {
  const key = "loonglab-theme";
  const toggle = document.querySelector("[data-theme-toggle]");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const root = document.documentElement;
      const current =
        root.getAttribute("data-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      const next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try {
        window.localStorage.setItem(key, next);
      } catch {
        // Ignore storage failures; the theme still applies to this page view.
      }
    });
  }

  document.querySelectorAll("[data-year]").forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });

  document.querySelectorAll("[data-copy]").forEach((block) => {
    const pre = block.querySelector("pre");
    if (!pre) return;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.textContent = "Copy";
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(pre.textContent);
        button.textContent = "Copied";
      } catch {
        button.textContent = "Copy failed";
      }
      setTimeout(() => (button.textContent = "Copy"), 1500);
    });
    block.style.position = "relative";
    button.style.position = "absolute";
    button.style.top = "0.5rem";
    button.style.right = "0.5rem";
    block.appendChild(button);
  });
})();
