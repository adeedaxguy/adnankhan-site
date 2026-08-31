(function () {
  "use strict";

  const root = document.documentElement;
  const grid = document.getElementById("workGrid");
  if (!grid) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  const layoutSequence = ["standard"];
  let observer;

  function allCards() {
    return Array.from(grid.querySelectorAll(".work-card"));
  }

  function visibleCards() {
    return allCards().filter((card) => !card.classList.contains("is-page-hidden"));
  }

  function addPointerDepth(link) {
    if (!finePointer.matches || reducedMotion.matches || link.dataset.depthReady === "true") return;
    link.dataset.depthReady = "true";
    const media = link.querySelector(".work-card-img");
    if (!media) return;

    link.addEventListener("pointermove", (event) => {
      const rect = link.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      media.style.setProperty("--portfolio-tilt-x", `${(x * 1.8).toFixed(2)}deg`);
      media.style.setProperty("--portfolio-tilt-y", `${(-y * 1.5).toFixed(2)}deg`);
    });

    link.addEventListener("pointerleave", () => {
      media.style.setProperty("--portfolio-tilt-x", "0deg");
      media.style.setProperty("--portfolio-tilt-y", "0deg");
    });
  }

  function prepareCards() {
    const cards = visibleCards();
    cards.forEach((card, index) => {
      const layout = layoutSequence[index % layoutSequence.length];
      const imageLink = card.querySelector(".work-card-img-link");
      card.dataset.layout = layout;
      if (imageLink) {
        imageLink.dataset.cardNumber = String((Number(card.dataset.index) || 0) + 1).padStart(2, "0");
        addPointerDepth(imageLink);
      }
      if (reducedMotion.matches) {
        card.classList.add("portfolio-card-visible");
      } else if (observer) {
        card.classList.remove("portfolio-card-visible");
        observer.observe(card);
      }
    });
  }

  function setupObserver() {
    if (reducedMotion.matches || !("IntersectionObserver" in window)) return;
    observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("portfolio-card-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -7% 0px", threshold: 0.08 });
  }

  setupObserver();
  root.classList.add("portfolio-motion-ready");
  document.addEventListener("portfolio:render", prepareCards);
  prepareCards();
})();
