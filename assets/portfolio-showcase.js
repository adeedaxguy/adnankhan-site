(function () {
  "use strict";

  const root = document.documentElement;
  const grid = document.getElementById("workGrid");
  if (!grid) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  const layoutSequence = ["standard"];
  let itemMap = new Map();
  let observer;

  function allCards() {
    return Array.from(grid.querySelectorAll(".work-card"));
  }

  function visibleCards() {
    return allCards().filter((card) => card.style.display !== "none");
  }

  function hydrateCard(card) {
    if (card.dataset.portfolioHydrated === "true") return;
    const caseLink = card.querySelector('.work-card-img-link[href*="/portfolio/"]');
    const designed = card.querySelector(".work-card-designed");
    if (!caseLink || !designed) return;

    const slug = caseLink.getAttribute("href").split("/").pop().replace(/\.html$/, "");
    const item = itemMap.get(slug);
    if (!item || !item.image) return;

    const fallback = designed.cloneNode(true);
    const image = document.createElement("img");
    image.src = item.image;
    image.alt = `${item.name} — ${item.platform || "website"} project`;
    image.loading = "lazy";
    image.decoding = "async";
    image.onerror = () => {
      image.replaceWith(fallback);
      card.dataset.portfolioHydrated = "fallback";
    };
    designed.replaceWith(image);
    card.dataset.portfolioHydrated = "true";
  }

  function hydrateAllCards() {
    if (!itemMap.size) return;
    allCards().forEach(hydrateCard);
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
    hydrateAllCards();
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

  async function loadPortfolioData() {
    try {
      const response = await fetch("/portfolio/portfolio.json", { credentials: "same-origin" });
      if (!response.ok) return;
      const data = await response.json();
      itemMap = new Map((data.items || []).map((item) => [item.slug, item]));
      hydrateAllCards();
      prepareCards();
    } catch (_error) {
      // The authored preview remains usable when JSON or an image is unavailable.
    }
  }

  setupObserver();
  root.classList.add("portfolio-motion-ready");
  document.addEventListener("portfolio:render", prepareCards);
  prepareCards();
  loadPortfolioData();
})();
