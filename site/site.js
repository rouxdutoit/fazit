(() => {
  const HERO_DELAY_MS = 150;
  const SCRAMBLE_STAGGER_MS = 800;
  const MAX_CHAR_STEP_MS = 18;
  const GLYPH_SWAP_MS = 42;
  const GLYPH_SETTLE_MS = 200;
  const REVEAL_STAGGER_MS = 80;
  const COPY_FEEDBACK_MS = 3000;

  const root = document.documentElement;
  const animate = matchMedia("(prefers-reduced-motion: no-preference)").matches;

  // Keep the original heading available to screen readers throughout the animation.
  const glyphs = "-_/\\|<>~^*+=:;!?#%&@0123456789";
  const randomGlyph = () => glyphs[Math.floor(Math.random() * glyphs.length)];

  const decode = (element) => {
    requestAnimationFrame((start) => {
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
      element.classList.add("scramble-started");

      const step = Math.min(MAX_CHAR_STEP_MS, SCRAMBLE_STAGGER_MS / Math.max(1, chars.length));
      let lastSwap = 0;
      const frame = (now) => {
        const elapsed = now - start;
        const swap = now - lastSwap > GLYPH_SWAP_MS;
        if (swap) lastSwap = now;
        let done = 0;
        chars.forEach((span, index) => {
          const from = index * step;
          if (elapsed >= from + GLYPH_SETTLE_MS) {
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
      frame(start);
    });
  };

  const observeOnce = (rootMargin, enter) => new IntersectionObserver((entries, observer) => {
    for (const { isIntersecting, target } of entries) {
      if (!isIntersecting) continue;
      observer.unobserve(target);
      enter(target);
    }
  }, { rootMargin });

  document.addEventListener("DOMContentLoaded", () => {
    const bar = document.querySelector("[data-bar]");
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

    const copy = document.querySelector("[data-copy]");
    if (copy) {
      const command = document.getElementById("demo-command");
      const message = document.querySelector(".copy-message");
      let reset;
      copy.hidden = false;
      copy.addEventListener("click", async () => {
        clearTimeout(reset);
        try {
          await navigator.clipboard.writeText(command.textContent);
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
        }
        reset = setTimeout(() => {
          copy.classList.remove("done");
          message.textContent = "";
        }, COPY_FEEDBACK_MS);
      });
    }
  }, { once: true });
  root.classList.add("has-js");

  if (animate) {
    const headings = observeOnce("0px 0px -8% 0px", decode);
    const reveal = observeOnce("0px 0px -6% 0px", (element) => {
      const grid = element.parentElement;
      if (grid.matches(".tiles, .figures")) {
        const columns = getComputedStyle(grid).gridTemplateColumns.split(" ").length;
        const column = [...grid.children].indexOf(element) % columns;
        element.style.setProperty("--reveal-delay", `${column * REVEAL_STAGGER_MS}ms`);
      }
      element.classList.add("in");
    });

    document.addEventListener("DOMContentLoaded", () => {
      for (const element of document.querySelectorAll("[data-scramble]")) {
        if (element.closest(".hero")) setTimeout(() => decode(element), HERO_DELAY_MS);
        else headings.observe(element);
      }
      for (const element of document.querySelectorAll(".tiles > li, .figures > li, .finding, .coverage, .timeline-step")) {
        reveal.observe(element);
      }
    }, { once: true });
    window.addEventListener("error", () => root.classList.remove("motion"), { once: true });
    root.classList.add("motion");
  }
})();
