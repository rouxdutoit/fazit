(() => {
  const root = document.documentElement;
  const systemTheme = matchMedia("(prefers-color-scheme: dark)");
  const storageKey = "fazit-theme";
  root.classList.add("js");

  try {
    const saved = localStorage.getItem(storageKey);
    if (saved === "light" || saved === "dark") root.dataset.theme = saved;
  } catch {
    // The system preference also works when browser storage is unavailable.
  }

  document.addEventListener("DOMContentLoaded", () => {
    const theme = document.querySelector("[data-theme-toggle]");
    const isDark = () => root.dataset.theme
      ? root.dataset.theme === "dark"
      : systemTheme.matches;

    if (theme) {
      const showTheme = () => theme.setAttribute("aria-pressed", String(isDark()));
      showTheme();
      theme.hidden = false;
      systemTheme.addEventListener("change", showTheme);
      theme.addEventListener("click", () => {
        root.dataset.theme = isDark() ? "light" : "dark";
        try {
          localStorage.setItem(storageKey, root.dataset.theme);
        } catch {
          // The choice still applies until the page is left.
        }
        showTheme();
      });
    }

    const menu = document.querySelector("[data-menu]");
    if (menu) {
      menu.querySelector("nav").addEventListener("click", (event) => {
        if (event.target.closest("a")) menu.open = false;
      });
      menu.addEventListener("focusout", (event) => {
        if (event.relatedTarget && !menu.contains(event.relatedTarget)) menu.open = false;
      });
      menu.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && menu.open) {
          menu.open = false;
          menu.querySelector("summary").focus();
        }
      });
    }

    const copy = document.querySelector("[data-copy]");
    if (copy) {
      const command = document.getElementById("demo-command");
      const message = document.querySelector(".copy-message");
      const label = copy.textContent;
      let reset;
      copy.hidden = false;
      copy.addEventListener("click", async () => {
        clearTimeout(reset);
        try {
          await navigator.clipboard.writeText(command.textContent);
          copy.textContent = copy.dataset.copied;
          message.textContent = copy.dataset.copied;
          message.classList.add("sr-only");
        } catch {
          const range = document.createRange();
          range.selectNodeContents(command);
          getSelection().removeAllRanges();
          getSelection().addRange(range);
          copy.textContent = label;
          message.classList.remove("sr-only");
          message.textContent = copy.dataset.manual;
        }
        reset = setTimeout(() => {
          copy.textContent = label;
          message.textContent = "";
        }, 3000);
      });
    }
  });
})();
