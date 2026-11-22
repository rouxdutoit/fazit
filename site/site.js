(() => {
  const COPY_FEEDBACK_MS = 3000;

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
          await navigator.clipboard.writeText(command.innerText);
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
  document.documentElement.classList.add("has-js");
})();
