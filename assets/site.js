const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
const EASE = "cubic-bezier(0.22, 1, 0.36, 1)";

// Menú móvil
(() => {
  const btn = document.querySelector(".nav-toggle");
  const nav = document.getElementById("nav");
  if (!btn || !nav) return;
  btn.addEventListener("click", () => {
    const open = btn.getAttribute("aria-expanded") === "true";
    btn.setAttribute("aria-expanded", String(!open));
    nav.classList.toggle("open", !open);
  });
  nav.addEventListener("click", (e) => {
    if (e.target.closest("a")) { btn.setAttribute("aria-expanded", "false"); nav.classList.remove("open"); }
  });
})();

// Preseleccionar servicio con ?servicio=boda|deporte|fallas|concierto|fiesta
(() => {
  const key = new URLSearchParams(location.search).get("servicio");
  if (!key) return;
  document.querySelectorAll('select[name="servicio"] option').forEach((o) => {
    if (o.dataset.key === key) o.selected = true;
  });
})();

// Envío del formulario sin salir de la página (si falla, se muestra el email)
document.querySelectorAll("form[data-ajax]").forEach((form) => {
  form.addEventListener("submit", async (e) => {
    if (!window.fetch) return;
    e.preventDefault();
    if (form.querySelector('[name="_honey"]').value) return;
    form.classList.add("sending");
    const err = form.querySelector(".form-error");
    err.hidden = true;
    try {
      const res = await fetch(form.action.replace("formsubmit.co/", "formsubmit.co/ajax/"), {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || String(data.success) === "false") throw new Error(data.message || res.status);
      location.href = form.querySelector('[name="_next"]').value;
    } catch (_) {
      form.classList.remove("sending");
      err.hidden = false;
    }
  });
});

// Aparición escalonada al hacer scroll
(() => {
  if (reduceMotion || !("IntersectionObserver" in window)) return;
  const groups = [
    ".section .eyebrow", ".section h2", ".section .lead", ".about-grid > div > p", ".about-grid .btn",
    ".service-card", ".gallery-item", ".steps li", ".audiences li", ".faq details",
    ".feature", ".form", ".about-img", ".logos li", ".ticks li", ".contact-list li", ".chips a",
    ".section > .wrap > .btn", ".footer-grid > div",
  ];
  const els = [...document.querySelectorAll(groups.join(","))];
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      en.target.classList.add("in");
      io.unobserve(en.target);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

  els.forEach((el) => {
    // Lo que ya se ve al cargar no se esconde (evita parpadeos)
    if (el.getBoundingClientRect().top < innerHeight * 0.92) return;
    // Retraso escalonado entre hermanos (galería, tarjetas, pasos…)
    const sibs = [...el.parentElement.children].filter((c) => c.tagName === el.tagName);
    const i = sibs.indexOf(el);
    const step = el.classList.contains("gallery-item") ? 0.07 : 0.09;
    el.style.setProperty("--d", `${Math.min(i % 6, 5) * step}s`);
    // Se oculta al instante (sin transición) y luego se reactiva la transición
    el.classList.add("rv", "rv-set");
    void getComputedStyle(el).opacity;
    el.classList.remove("rv-set");
    // Al terminar, se quita la clase para que vuelvan los hovers normales
    el.addEventListener("transitionend", function done(ev) {
      if (ev.target !== el || ev.propertyName !== "transform") return;
      el.classList.remove("rv", "in");
      el.style.removeProperty("--d");
      el.removeEventListener("transitionend", done);
    });
    io.observe(el);
  });
})();

// Parallax suave en las portadas + cabecera al hacer scroll
(() => {
  const header = document.querySelector(".site-header");
  const hero = document.querySelector(".hero, .page-hero");
  const media = hero && hero.querySelector(".hero-media, .page-hero-img");
  const copy = hero && hero.querySelector(".hero-copy, .page-hero-copy");
  let ticking = false;
  const update = () => {
    ticking = false;
    const y = scrollY;
    header && header.classList.toggle("scrolled", y > 12);
    if (reduceMotion || !hero) return;
    const h = hero.offsetHeight;
    if (y > h) return;
    const p = y / h;
    if (media) media.style.transform = `translate3d(0, ${y * 0.35}px, 0)` + (media.tagName === "IMG" ? " scale(1.04)" : "");
    if (copy) {
      copy.style.transform = `translate3d(0, ${y * 0.18}px, 0)`;
      copy.style.opacity = String(Math.max(0, 1 - p * 1.4));
    }
  };
  addEventListener("scroll", () => {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  update();
})();

// Visor de fotos (se amplía desde la miniatura)
(() => {
  const dlg = document.querySelector("dialog.lightbox");
  if (!dlg || !dlg.showModal) return;
  const img = dlg.querySelector("img");
  const cap = dlg.querySelector(".lb-caption");
  let items = [], i = 0;

  const fit = (thumb) => {
    const r = thumb.naturalWidth / thumb.naturalHeight || 1.5;
    const maxW = innerWidth * 0.92, maxH = innerHeight * 0.84;
    const w = Math.min(maxW, maxH * r);
    img.style.width = `${w}px`;
    img.style.height = `${w / r}px`;
  };

  const load = (a) => {
    const t = a.querySelector("img");
    img.src = t.currentSrc || t.src; // primero la miniatura (instantánea)
    img.alt = t.alt;
    cap.textContent = t.alt;
    fit(t);
    const big = new Image();
    big.onload = () => { if (items[i] === a) img.src = a.href; };
    big.src = a.href;
  };

  const show = (n, dir = 0) => {
    i = (n + items.length) % items.length;
    load(items[i]);
    if (dir && !reduceMotion) {
      img.animate([{ opacity: 0, transform: `translateX(${dir * 40}px)` }, { opacity: 1, transform: "none" }],
        { duration: 450, easing: EASE });
    }
  };

  const zoomFrom = (thumb) => {
    if (reduceMotion) return;
    const a = thumb.getBoundingClientRect();
    const b = img.getBoundingClientRect();
    if (!a.width || !b.width) return;
    const dx = a.left + a.width / 2 - (b.left + b.width / 2);
    const dy = a.top + a.height / 2 - (b.top + b.height / 2);
    const s = Math.max(a.width / b.width, a.height / b.height);
    img.animate([
      { transform: `translate(${dx}px, ${dy}px) scale(${s})`, borderRadius: "10px" },
      { transform: "none", borderRadius: "6px" },
    ], { duration: 650, easing: EASE });
  };

  document.addEventListener("click", (e) => {
    const a = e.target.closest("a[data-lightbox]");
    if (!a) return;
    e.preventDefault();
    items = [...a.closest("[data-gallery]").querySelectorAll("a[data-lightbox]")];
    show(items.indexOf(a));
    dlg.showModal();
    zoomFrom(a.querySelector("img"));
  });

  const close = () => {
    if (reduceMotion || dlg.classList.contains("closing")) { dlg.close(); return; }
    dlg.classList.add("closing");
    img.animate([{ transform: "none", opacity: 1 }, { transform: "scale(0.94)", opacity: 0 }],
      { duration: 280, easing: "ease-in" }).onfinish = () => { dlg.classList.remove("closing"); dlg.close(); };
  };

  dlg.querySelector(".lb-close").addEventListener("click", close);
  dlg.querySelector(".lb-prev").addEventListener("click", () => show(i - 1, -1));
  dlg.querySelector(".lb-next").addEventListener("click", () => show(i + 1, 1));
  dlg.addEventListener("click", (e) => { if (e.target === dlg) close(); });
  dlg.addEventListener("cancel", (e) => { e.preventDefault(); close(); });
  dlg.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") show(i + 1, 1);
    if (e.key === "ArrowLeft") show(i - 1, -1);
  });
  let x0 = null;
  dlg.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  dlg.addEventListener("touchend", (e) => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(dx < 0 ? i + 1 : i - 1, dx < 0 ? 1 : -1);
    x0 = null;
  });
  addEventListener("resize", () => { if (dlg.open && items[i]) fit(items[i].querySelector("img")); });
  dlg.addEventListener("close", () => { img.removeAttribute("src"); });
})();
