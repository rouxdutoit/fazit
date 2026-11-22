(() => {
  const COPY_FEEDBACK_MS = 3000;
  const SCRAMBLE_DELAY_MS = 150;
  const CHAR_STEP_MS = 18;
  const GLYPH_SWAP_MS = 42;
  const GLYPH_SETTLE_MS = 200;
  const GLYPHS = "-_/\\|<>~^*+=:;!?#%&@0123456789";

  const root = document.documentElement;
  const animate = matchMedia("(prefers-reduced-motion: no-preference)").matches;
  // Brand signature: the bar's wordmark decodes when a visitor arrives from elsewhere, the footer's as it comes into view.
  // The links keep their labels for screen readers.
  const scrambleWordmark = animate && !document.referrer.startsWith(location.origin);

  const decode = (element) => {
    requestAnimationFrame((start) => {
      const text = element.textContent;
      const chars = [...text].map((char) => {
        const span = document.createElement("span");
        span.className = "ch wait";
        span.textContent = char;
        return span;
      });
      element.replaceChildren(...chars);
      element.classList.add("scramble-started");

      let lastSwap = 0;
      const frame = (now) => {
        const elapsed = now - start;
        const swap = now - lastSwap > GLYPH_SWAP_MS;
        if (swap) lastSwap = now;
        let done = 0;
        chars.forEach((span, index) => {
          const from = index * CHAR_STEP_MS;
          if (elapsed >= from + GLYPH_SETTLE_MS) {
            span.className = "ch";
            done += 1;
          } else if (elapsed >= from && (swap || span.classList.contains("wait"))) {
            span.className = "ch sg";
            span.dataset.g = GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
          }
        });
        if (done < chars.length) requestAnimationFrame(frame);
        else element.textContent = text;
      };
      frame(start);
    });
  };

  if (scrambleWordmark) {
    root.classList.add("scramble");
    window.addEventListener("error", () => root.classList.remove("scramble"), { once: true });
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (scrambleWordmark) {
      const wordmark = document.querySelector(".bar .wordmark");
      setTimeout(() => decode(wordmark), SCRAMBLE_DELAY_MS);
    }
    const footWordmark = document.querySelector("footer .wordmark");
    if (animate && footWordmark) {
      new IntersectionObserver((entries, observer) => {
        if (!entries.some((entry) => entry.isIntersecting)) return;
        observer.disconnect();
        decode(footWordmark);
      }).observe(footWordmark);
    }

    const bar = document.querySelector(".bar");
    const menuButton = bar.querySelector(".menu-button");
    const setOpen = (open) => {
      menuButton.setAttribute("aria-expanded", String(open));
      bar.toggleAttribute("data-open", open);
    };
    menuButton.hidden = false;
    menuButton.addEventListener("click", () => setOpen(!bar.hasAttribute("data-open")));
    bar.querySelector("nav").addEventListener("click", (event) => {
      if (event.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && bar.hasAttribute("data-open")) {
        setOpen(false);
        menuButton.focus();
      }
    });
    matchMedia("(min-width: 820px)").addEventListener("change", () => setOpen(false));

    for (const copy of document.querySelectorAll("[data-copy]")) {
      const block = copy.closest(".command");
      const command = block?.querySelector("code");
      const message = block?.querySelector(".copy-message");
      if (!command || !message) continue;
      let reset;
      let pending = false;
      copy.hidden = false;
      copy.addEventListener("click", async () => {
        if (pending) return;
        pending = true;
        clearTimeout(reset);
        copy.classList.remove("done");
        message.textContent = "";
        try {
          const lines = Array.from(command.children, (line) => line.textContent);
          await navigator.clipboard.writeText(lines.join("\n"));
          copy.classList.add("done");
          message.classList.add("sr-only");
          message.textContent = copy.dataset.copied;
        } catch {
          const range = document.createRange();
          range.selectNodeContents(command);
          getSelection().removeAllRanges();
          getSelection().addRange(range);
          message.classList.remove("sr-only");
          message.textContent = copy.dataset.manual;
        } finally {
          pending = false;
        }
        reset = setTimeout(() => {
          copy.classList.remove("done");
          message.textContent = "";
        }, COPY_FEEDBACK_MS);
      });
    }
  }, { once: true });
  root.classList.add("has-js");
})();
