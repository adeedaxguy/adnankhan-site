(function () {
  "use strict";

  var root = document.querySelector("[data-review-archive]");
  if (!root) return;

  var grid = root.querySelector("[data-review-grid]");
  var count = root.querySelector("[data-review-count]");
  var shown = root.querySelector("[data-review-shown]");
  var search = root.querySelector("[data-review-search]");
  var loadMore = root.querySelector("[data-review-more]");
  var filters = Array.prototype.slice.call(root.querySelectorAll("[data-review-filter]"));
  var allReviews = [];
  var visibleReviews = [];
  var pageSize = 24;
  var limit = pageSize;
  var activeProfile = "all";
  var query = "";

  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (typeof text === "string") node.textContent = text;
    return node;
  }

  function normalize(value) {
    return String(value || "").toLowerCase().trim();
  }

  function ratingLabel(rating) {
    var numeric = Number(rating);
    return numeric.toFixed(1) + " / 5";
  }

  function dateValue(value) {
    var parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? "" : parsed.toISOString().slice(0, 10);
  }

  function createCard(review) {
    var card = element("article", "review-archive-card");
    var head = element("div", "review-archive-card__head");
    var rating = element("span", "review-archive-card__rating", ratingLabel(review.rating));
    var date = element("time", "review-archive-card__date", review.date);
    var quote = element("blockquote", "", review.comment);
    var footer = element("footer", "review-archive-card__footer");
    var client = element("span", "review-archive-card__client", review.client || "Upwork client");
    var project = element("span", "review-archive-card__project", review.project);
    var source = element("a", "review-archive-card__source", "Source: " + review.profileName + " on Upwork ↗");

    rating.setAttribute("aria-label", ratingLabel(review.rating) + " out of 5 stars");
    if (dateValue(review.date)) date.setAttribute("datetime", dateValue(review.date));
    source.href = review.profileUrl;
    source.target = "_blank";
    source.rel = "noopener noreferrer";
    source.setAttribute("aria-label", "Open " + review.profileName + "'s Upwork profile in a new tab");

    head.appendChild(rating);
    head.appendChild(date);
    footer.appendChild(client);
    footer.appendChild(project);
    footer.appendChild(source);
    card.appendChild(head);
    card.appendChild(quote);
    card.appendChild(footer);
    return card;
  }

  function filteredReviews() {
    return allReviews.filter(function (review) {
      var profileMatches = activeProfile === "all" || review.profile === activeProfile;
      if (!profileMatches) return false;
      if (!query) return true;
      var haystack = normalize([
        review.comment,
        review.client,
        review.project,
        review.profileName,
        review.date
      ].join(" "));
      return haystack.indexOf(query) !== -1;
    });
  }

  function updateUrl() {
    if (!window.history || !window.history.replaceState) return;
    var params = new URLSearchParams(window.location.search);
    if (activeProfile === "all") params.delete("profile");
    else params.set("profile", activeProfile);
    if (query) params.set("q", query);
    else params.delete("q");
    var next = window.location.pathname + (params.toString() ? "?" + params.toString() : "") + window.location.hash;
    window.history.replaceState(null, "", next);
  }

  function render() {
    visibleReviews = filteredReviews();
    var fragment = document.createDocumentFragment();
    var current = visibleReviews.slice(0, limit);

    grid.replaceChildren();
    if (!current.length) {
      fragment.appendChild(element("p", "reviews-empty", "No feedback matches this search. Try a broader phrase or choose both profiles."));
    } else {
      current.forEach(function (review) {
        fragment.appendChild(createCard(review));
      });
    }
    grid.appendChild(fragment);
    grid.setAttribute("aria-busy", "false");

    count.textContent = visibleReviews.length + (visibleReviews.length === 1 ? " review" : " reviews");
    shown.textContent = current.length ? "Showing " + current.length : "Showing none";
    loadMore.hidden = current.length >= visibleReviews.length;
    if (!loadMore.hidden) {
      loadMore.textContent = "Show " + Math.min(pageSize, visibleReviews.length - current.length) + " more";
    }
  }

  function setProfile(profile) {
    activeProfile = profile;
    limit = pageSize;
    filters.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.reviewFilter === profile));
    });
    updateUrl();
    render();
  }

  function loadInitialState() {
    var params = new URLSearchParams(window.location.search);
    var requestedProfile = params.get("profile");
    if (requestedProfile === "irfankhan" || requestedProfile === "wordpressandshopifydeveloper") {
      activeProfile = requestedProfile;
    }
    query = normalize(params.get("q"));
    search.value = params.get("q") || "";
  }

  filters.forEach(function (button) {
    button.addEventListener("click", function () {
      setProfile(button.dataset.reviewFilter);
    });
  });

  var searchTimer;
  search.addEventListener("input", function () {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(function () {
      query = normalize(search.value);
      limit = pageSize;
      updateUrl();
      render();
    }, 160);
  });

  loadMore.addEventListener("click", function () {
    limit += pageSize;
    render();
  });

  fetch("/assets/reviews.json")
    .then(function (response) {
      if (!response.ok) throw new Error("Review archive could not be loaded.");
      return response.json();
    })
    .then(function (payload) {
      allReviews = Array.isArray(payload.reviews) ? payload.reviews : [];
      loadInitialState();
      setProfile(activeProfile);
    })
    .catch(function () {
      grid.setAttribute("aria-busy", "false");
      grid.replaceChildren(element("p", "reviews-error", "The review archive is temporarily unavailable. The two verified Upwork profiles remain linked above."));
      count.textContent = "Archive unavailable";
      shown.textContent = "";
      loadMore.hidden = true;
    });
}());
