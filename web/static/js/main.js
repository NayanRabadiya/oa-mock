"use strict";
// Global listeners and first render. Loaded last.

document.addEventListener("visibilitychange", () => { if (document.hidden && S.view === "exam" && S.exam && !S.exam.practice && !S.exam.ended){ S.exam.switches++; saveExam(); } });
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && !$("#modal").hidden) closeModal();
  if (e.altKey && (e.key === "ArrowLeft" || e.key === "ArrowRight") && S.view === "exam" && S.exam && !S.exam.ended){ e.preventDefault(); goQ(S.exam, S.exam.cur + (e.key === "ArrowRight" ? 1 : -1)); }
});
window.addEventListener("beforeunload", saveCode);
render();
