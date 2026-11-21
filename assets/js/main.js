document.addEventListener("DOMContentLoaded", () => {
  /* ---------- Data: mapa gallery images ---------- */
  const MAP_IDS = [
    "002","003","004","005","006","007","008","009",
    "010","011","012","013","014","015","016","017",
  ];

  /* Carrossel de matérias: um mapa real por cartão (materia-01..16.webp, ordem do tools/montar-imagens.py) */
  const SUBJECTS = [
    "Português: ideia central e argumentação", "Português: conectivos", "Informática: sistemas operacionais",
    "Informática: Linux", "Raciocínio Lógico: condicional", "Raciocínio Lógico: quantificadores",
    "Direito Penal: lei penal no tempo", "Direito Penal: territorialidade", "Processo Penal: lei processual",
    "Processo Penal: indiciamento", "Abuso de Autoridade", "Lei de Tortura", "Processo Penal: diligências",
    "Constitucional: aplicabilidade", "Constitucional: igualdade", "Constitucional: direito à vida",
  ];

  /* ---------- Top bar date ---------- */
  const dateEl = document.getElementById("topbar-date");
  if (dateEl) {
    const d = new Date();
    const dd = String(d.getDate()).padStart(2, "0");
    const mm = String(d.getMonth() + 1).padStart(2, "0");
    dateEl.textContent = `${dd}/${mm}/${d.getFullYear()}`;
  }

  /* ---------- Marquee 1: mapa gallery ---------- */
  const track1 = document.getElementById("marquee-1-track");
  if (track1) {
    const list = MAP_IDS;
    const build = () =>
      list
        .map((id) => `<img src="/assets/img/mapa-${id}.webp" alt="Mapa da Aprovação PC-TO: exemplo de página do material" loading="lazy" />`)
        .join("");
    track1.innerHTML = build() + build();
  }

  /* ---------- Marquee 2: benefit badges ---------- */
  const track2 = document.getElementById("marquee-2-track");
  if (track2) {
    const build = () =>
      SUBJECTS.map(
        (s, n) => `
        <div class="marquee-badge">
          <div class="marquee-badge__head">
            <span class="marquee-badge__top">PC-TO INVESTIGADOR</span>
            <span class="marquee-badge__mid">MAPA DA APROVAÇÃO</span>
          </div>
          <div class="marquee-badge__tablet">
            <img src="/assets/img/materia-${String(n % SUBJECTS.length + 1).padStart(2, "0")}.webp?v=7" alt="Mapa da Aprovação PC-TO: ${s}" loading="lazy" />
          </div>
          <span class="marquee-badge__subject">${s}</span>
        </div>`
      ).join("");
    track2.innerHTML = build() + build();
  }

  /* ---------- Stack art (mockup do produto) ---------- */
  document.querySelectorAll(".stack-art").forEach((el) => {
    el.innerHTML = '<img src="/assets/img/mockup-produto.webp?v=9" alt="Mapa da Aprovação PC-TO: 290 mapas visuais e 4 bônus" loading="lazy" />';
  });

  /* ---------- Marquee controls (pause / prev / next) ---------- */
  document.querySelectorAll("[data-marquee-toggle]").forEach((btn) => {
    const target = document.getElementById(btn.dataset.marqueeToggle);
    btn.addEventListener("click", () => {
      target.classList.toggle("is-paused");
      btn.textContent = target.classList.contains("is-paused") ? "Continuar" : "Pausar";
    });
  });

  const nudgeMarquee = (id, dir) => {
    const track = document.getElementById(`${id}-track`);
    if (!track) return;
    track.style.animationPlayState = "paused";
    const wrapper = document.getElementById(id);
    wrapper.classList.add("is-paused");
    const current = getComputedStyle(track).transform;
    let x = 0;
    if (current && current !== "none") {
      const m = new DOMMatrixReadOnly(current);
      x = m.m41;
    }
    track.style.transition = "transform 0.35s ease";
    track.style.transform = `translateX(${x + dir * -220}px)`;
  };

  document.querySelectorAll("[data-marquee-prev]").forEach((btn) => {
    btn.addEventListener("click", () => nudgeMarquee(btn.dataset.marqueePrev, -1));
  });
  document.querySelectorAll("[data-marquee-next]").forEach((btn) => {
    btn.addEventListener("click", () => nudgeMarquee(btn.dataset.marqueeNext, 1));
  });

  /* ---------- Drag compare slider (só arrasta pelo ícone central) ---------- */
  const compare = document.getElementById("compare");
  const before = document.getElementById("compare-before");
  const handle = document.getElementById("compare-handle");
  if (compare && before && handle) {
    compare.querySelectorAll("img").forEach((img) => (img.draggable = false));

    const setPosition = (clientX) => {
      const rect = compare.getBoundingClientRect();
      let pct = ((clientX - rect.left) / rect.width) * 100;
      pct = Math.max(4, Math.min(96, pct));
      before.style.clipPath = `inset(0 ${100 - pct}% 0 0)`;
      handle.style.left = `${pct}%`;
    };

    let active = false;
    handle.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      active = true;
      try { handle.setPointerCapture(e.pointerId); } catch (_) {}
      handle.classList.add("is-dragging");
    });
    handle.addEventListener("pointermove", (e) => {
      if (active) setPosition(e.clientX);
    });
    const stop = (e) => {
      active = false;
      try { handle.releasePointerCapture(e.pointerId); } catch (_) {}
      handle.classList.remove("is-dragging");
    };
    handle.addEventListener("pointerup", stop);
    handle.addEventListener("pointercancel", stop);
  }

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll(".faq-item__q").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".faq-item");
      const answer = item.querySelector(".faq-item__a");
      const isOpen = item.classList.contains("is-open");

      document.querySelectorAll(".faq-item.is-open").forEach((openItem) => {
        if (openItem !== item) {
          openItem.classList.remove("is-open");
          openItem.querySelector(".faq-item__a").style.maxHeight = null;
        }
      });

      item.classList.toggle("is-open", !isOpen);
      answer.style.maxHeight = !isOpen ? `${answer.scrollHeight}px` : null;
    });
  });
});

/* ---------- Contagem até a data prevista do edital (04/12/2026) ---------- */
(function () {
  const alvo = new Date("2026-12-04T00:00:00-03:00");
  const atualizar = () => {
    const ms = alvo - new Date();
    const dias = Math.max(0, Math.ceil(ms / 86400000));
    document.querySelectorAll("[data-dias-edital]").forEach((el) => {
      el.textContent = dias === 0 ? "a qualquer momento" : dias === 1 ? "1 dia" : `${dias} dias`;
    });
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", atualizar);
  else atualizar();
})();
