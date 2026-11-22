(() => {
  const root = document.documentElement;
  const animate = !matchMedia("(prefers-reduced-motion: reduce)").matches
    && "IntersectionObserver" in window;
  root.classList.add("has-js");
  if (animate) root.classList.add("motion");

  // Headings resolve from random glyphs into their text, like evidence into a conclusion.
  // Screen readers get the plain text throughout; reduced motion skips the effect.
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

      const step = Math.min(18, 800 / Math.max(1, chars.length));
      let lastSwap = 0;
      const frame = (now) => {
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
      frame(start);
    });
  };

  document.addEventListener("DOMContentLoaded", () => {
    const bar = document.querySelector("[data-bar]");
    const menuButton = bar?.querySelector(".menu-button");
    if (menuButton) {
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
    }

    if (animate) {
      const observer = new IntersectionObserver((entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          observer.unobserve(entry.target);
          decode(entry.target);
        }
      }, { rootMargin: "0px 0px -8% 0px" });
      for (const element of document.querySelectorAll("[data-scramble]")) {
        if (element.closest(".hero")) setTimeout(() => decode(element), 150);
        else observer.observe(element);
      }

      // Content rises into place as it enters, a beat apart within a row.
      const reveal = new IntersectionObserver((entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          reveal.unobserve(entry.target);
          entry.target.classList.add("in");
        }
      }, { rootMargin: "0px 0px -6% 0px" });
      for (const element of document.querySelectorAll(".tiles > li, .figures > li, .finding, .table-wrap, .timeline-step")) {
        element.classList.add("reveal");
        element.style.setProperty("--i", [...element.parentElement.children].indexOf(element) % 3);
        reveal.observe(element);
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
          copy.classList.add("done");
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
          copy.classList.remove("done");
          message.textContent = "";
        }, 3000);
      });
    }
  });
})();
