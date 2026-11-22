(() => {
  const root = document.documentElement;
  const systemTheme = matchMedia("(prefers-color-scheme: dark)");
  const storageKey = "fazit-theme";
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  const animate = !reducedMotion.matches && "IntersectionObserver" in window;
  if (animate) root.classList.add("js");

  try {
    const saved = localStorage.getItem(storageKey);
    if (saved === "light" || saved === "dark") root.dataset.theme = saved;
  } catch {
    // The system preference also works when browser storage is unavailable.
  }

  // Headings resolve from random glyphs into their text, like evidence into a conclusion.
  // Screen readers get the plain text throughout; reduced motion skips the effect.
  const glyphs = "-_/\\|<>~^*+=:;!?#%&@0123456789";
  const randomGlyph = () => glyphs[Math.floor(Math.random() * glyphs.length)];
  const prepared = new WeakMap();

  const prepare = (element) => {
    const text = element.textContent;
    const plain = document.createElement("span");
    const shown = document.createElement("span");
    const chars = [];
    plain.className = "sr-only";
    plain.textContent = text;
    shown.setAttribute("aria-hidden", "true");
    for (const char of text) {
      if (/\s/.test(char)) {
        shown.append(char);
        continue;
      }
      const span = document.createElement("span");
      span.className = "ch wait";
      span.textContent = char;
      shown.append(span);
      chars.push(span);
    }
    element.replaceChildren(plain, shown);
    element.classList.add("ready");
    prepared.set(element, { text, chars });
  };

  const decode = (element, delay) => {
    const { text, chars } = prepared.get(element);
    const step = Math.min(18, 800 / Math.max(1, chars.length));
    let start = 0;
    let lastSwap = 0;
    const frame = (now) => {
      start ||= now;
      const elapsed = now - start;
      const swap = now - lastSwap > 42;
      if (swap) lastSwap = now;
      let done = 0;
      chars.forEach((span, index) => {
        const from = index * step;
        if (elapsed >= from + 200) {
          span.className = "ch";
          done += 1;
        } else if (elapsed >= from && (swap || span.classList.contains("wait"))) {
          span.className = "ch sg";
          span.dataset.g = randomGlyph();
        }
      });
      if (done < chars.length) requestAnimationFrame(frame);
      else element.textContent = text;
    };
    setTimeout(() => requestAnimationFrame(frame), delay);
  };

  document.addEventListener("DOMContentLoaded", () => {
    const theme = document.querySelector("[data-theme-toggle]");
    const isDark = () => root.dataset.theme
      ? root.dataset.theme === "dark"
      : systemTheme.matches;

    if (theme) {
      const darkPreviews = document.querySelectorAll("[data-dark-preview]");
      const showTheme = () => {
        const dark = isDark();
        theme.setAttribute("aria-pressed", String(dark));
        if (!root.dataset.theme) return;
        for (const source of darkPreviews) {
          source.media = dark ? (source.dataset.darkPreview || "all") : "not all";
        }
      };
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

    if (animate) {
      try {
        const targets = [...document.querySelectorAll("[data-scramble]")];
        const observer = new IntersectionObserver((entries) => {
          for (const entry of entries) {
            if (!entry.isIntersecting) continue;
            observer.unobserve(entry.target);
            decode(entry.target, 0);
          }
        }, { rootMargin: "0px 0px -8% 0px" });
        for (const element of targets) {
          prepare(element);
          if (element.closest(".hero")) decode(element, 150);
          else observer.observe(element);
        }
      } catch {
        root.classList.remove("js");
      }
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
