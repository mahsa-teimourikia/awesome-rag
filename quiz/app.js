import { gradeQuiz } from "./grading.js";
import { questions } from "./questions.js";
import { allLessons, learningPath } from "./learning.js";

const storageKey = "awesome-rag-quiz-selections-v1";
const repositoryContentBase =
  "https://github.com/mahsa-teimourikia/awsome-rag/blob/main/";

const elements = {
  answeredCount: document.querySelector("#answered-count"),
  categoryList: document.querySelector("#category-list"),
  form: document.querySelector("#quiz-form"),
  progressTotal: document.querySelector("#progress-total"),
  progressTrack: document.querySelector("#progress-track"),
  questionCount: document.querySelector("#question-count"),
  questionList: document.querySelector("#question-list"),
  resetButton: document.querySelector("#reset-button"),
  results: document.querySelector("#results"),
  reviewButton: document.querySelector("#review-button"),
  retryButton: document.querySelector("#retry-button"),
  scoreHeading: document.querySelector("#score-heading"),
  scorePercent: document.querySelector("#score-percent"),
  scoreSummary: document.querySelector("#score-summary"),
  topicScores: document.querySelector("#topic-scores"),
  learningPathList: document.querySelector("#learning-path-list"),
  exportProgress: document.querySelector("#export-progress"),
  importProgress: document.querySelector("#import-progress"),
  resetLearningProgress: document.querySelector("#reset-learning-progress"),
  progressFile: document.querySelector("#progress-file"),
  quizContext: document.querySelector("#quiz-context"),
  levelProgressGrid: document.querySelector("#level-progress-grid"),
  levelFilter: document.querySelector("#level-filter"),
  lessonFilter: document.querySelector("#lesson-filter"),
  clearFilters: document.querySelector("#clear-filters"),
  lessonDetail: document.querySelector("#lesson-detail"),
  resumeBanner: document.querySelector("#resume-banner"),
};

let selections = loadSelections();
let latestGrade = null;
let showingReview = false;

function loadSelections() {
  try {
    const stored = JSON.parse(localStorage.getItem(storageKey) ?? "{}");
    return typeof stored === "object" && stored !== null ? stored : {};
  } catch {
    return {};
  }
}

function saveSelections() {
  localStorage.setItem(storageKey, JSON.stringify(selections));
}

function activeQuestions() {
  const checkpointId = window.location.hash.replace(/^#quiz-/, "");
  const lesson = allLessons.find((item) => item.id === checkpointId);
  return lesson ? questions.filter((question) => question.category === lesson.category) : questions;
}

function answeredTotal() {
  return activeQuestions().filter((question) => (selections[question.id] ?? []).length > 0)
    .length;
}

function categorySlug(category) {
  return category.toLowerCase().replaceAll(/\s+/g, "-");
}

function renderCategoryList() {
  const counts = activeQuestions().reduce((result, question) => {
    result[question.category] = (result[question.category] ?? 0) + 1;
    return result;
  }, {});

  elements.categoryList.innerHTML = Object.entries(counts)
    .map(
      ([category, count]) => `
        <a class="category-link" href="#category-${categorySlug(category)}">
          <span>${category}</span>
          <span>${count}</span>
        </a>
      `,
    )
    .join("");
}

function renderLearningPath() {
  const level = elements.levelFilter.value;
  const query = elements.lessonFilter.value.trim().toLowerCase();
  const visible = (module, track) => (level === "all" || track.id === level) && (!query || `${module.title} ${module.description} ${module.technologies.join(" ")}`.toLowerCase().includes(query));
  elements.levelProgressGrid.innerHTML = learningPath.map((track) => {
    const completed = track.modules.filter((module) => isLessonComplete(module.id)).length;
    const scores = track.modules.map((module) => progress.quizScores?.[module.id]).filter((score) => typeof score === "number");
    const average = scores.length ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : null;
    const percent = Math.round((completed / track.modules.length) * 100);
    return `<a class="level-progress-card ${track.tone}" href="#${track.id}"><div><span class="level-pill">${track.level}</span><strong>${completed}/${track.modules.length}</strong></div><progress max="100" value="${percent}">${percent}%</progress><span>${average === null ? "No checkpoint scores yet" : `Average checkpoint: ${average}%`}</span></a>`;
  }).join("");
  elements.learningPathList.innerHTML = learningPath.map((track) => {
    const modules = track.modules.filter((module) => visible(module, track));
    if (!modules.length) return "";
    return `
    <section class="learning-track ${track.tone}" id="${track.id}">
      <div class="track-heading"><div><span class="level-pill">${track.level}</span><h3>${track.outcome}</h3></div><span class="track-count">${modules.length} matching steps</span></div>
      <ol class="learning-modules">${modules.map((module, index) => `
        <li class="learning-module" id="lesson-${module.id}"><span class="module-number">${index + 1}</span><div><h4><a class="lesson-title" href="#lesson-${module.id}">${module.title}</a></h4><p>${module.description}</p><div class="module-meta"><span>${module.minutes} min</span>${module.technologies.map((technology) => `<span>${technology}</span>`).join("")}${progress.quizScores?.[module.id] !== undefined ? `<span class="score-badge">Score ${progress.quizScores[module.id]}%</span>` : ""}</div><div class="module-links"><a href="${module.material}">Read lesson</a><a href="${module.notebook}">Open notebook</a><a href="#quiz-${module.id}">Quiz checkpoint</a><button class="complete-button" data-lesson-id="${module.id}" type="button">${isLessonComplete(module.id) ? "Completed" : "Mark complete"}</button></div></div></li>
      `).join("")}</ol>
    </section>
  `;
  }).join("");
  document.querySelector("#learning-progress").textContent = `${progress.completedLessons?.length ?? 0}/${allLessons.length} lessons complete`;
  const next = allLessons.find((lesson) => !isLessonComplete(lesson.id));
  if (next) {
    elements.resumeBanner.hidden = false;
    elements.resumeBanner.innerHTML = `<span><strong>${progress.lastVisited ? "Continue your path" : "Start your path"}</strong><small>Recommended next: ${next.title}</small></span><a class="primary-button" href="#lesson-${next.id}">${progress.lastVisited ? "Resume lesson" : "Begin lesson"} →</a>`;
  } else {
    elements.resumeBanner.hidden = false;
    elements.resumeBanner.innerHTML = `<span><strong>Learning path complete</strong><small>Revisit any lesson or retake a checkpoint to reinforce your skills.</small></span><a class="secondary-button" href="#learning-path">Review the path</a>`;
  }
}

const progressKey = "awesome-rag-learning-progress-v1";
function loadProgress() { try { return JSON.parse(localStorage.getItem(progressKey) ?? "{}"); } catch { return {}; } }
let progress = loadProgress();
function isLessonComplete(id) { return progress.completedLessons?.includes(id); }
function saveProgress() { localStorage.setItem(progressKey, JSON.stringify(progress)); }
function bindLearningActions() {
  document.querySelectorAll(".complete-button").forEach((button) => button.addEventListener("click", () => {
    const id = button.dataset.lessonId;
    progress.completedLessons = [...new Set([...(progress.completedLessons ?? []), id])];
    progress.lastVisited = id;
    saveProgress();
    button.textContent = "Completed";
    button.classList.add("is-complete");
  }));
}

function refreshLearningPath() { renderLearningPath(); bindLearningActions(); }
elements.exportProgress.addEventListener("click", () => {
  const payload = { version: 2, exportedAt: new Date().toISOString(), completedLessons: progress.completedLessons ?? [], lastVisited: progress.lastVisited ?? null, quizScores: progress.quizScores ?? {} };
  const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" })); link.download = "awesome-rag-progress.json"; link.click(); URL.revokeObjectURL(link.href);
});
elements.importProgress.addEventListener("click", () => elements.progressFile.click());
elements.progressFile.addEventListener("change", async () => {
  const file = elements.progressFile.files?.[0]; if (!file) return;
  try { const imported = JSON.parse(await file.text()); if (!Array.isArray(imported.completedLessons)) throw new Error("Invalid progress file"); progress = { completedLessons: imported.completedLessons.filter((id) => allLessons.some((lesson) => lesson.id === id)), lastVisited: allLessons.some((lesson) => lesson.id === imported.lastVisited) ? imported.lastVisited : null, quizScores: Object.fromEntries(Object.entries(imported.quizScores ?? {}).filter(([id, score]) => allLessons.some((lesson) => lesson.id === id) && Number.isFinite(score))) }; saveProgress(); refreshLearningPath(); } catch { window.alert("That progress file could not be imported."); } finally { elements.progressFile.value = ""; }
});
elements.resetLearningProgress.addEventListener("click", () => { if (!window.confirm("Reset completed lessons and learning progress?")) return; progress = {}; saveProgress(); refreshLearningPath(); });

function showLessonFromHash() {
  const quizId = window.location.hash.replace(/^#quiz-/, "");
  const quizLesson = allLessons.find((item) => item.id === quizId);
  if (quizLesson) {
    elements.quizContext.hidden = false;
    elements.quizContext.innerHTML = `<strong>Checkpoint: ${quizLesson.title}</strong><span>This checkpoint contains the ${quizLesson.category} questions that match this lesson.</span><a href="#lesson-${quizLesson.id}">Return to lesson</a>`;
    elements.quizContext.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  elements.quizContext.hidden = true;
  const id = window.location.hash.replace(/^#lesson-/, "");
  const lesson = allLessons.find((item) => item.id === id);
  if (!lesson) { elements.lessonDetail.hidden = true; return; }
  progress.lastVisited = lesson.id;
  saveProgress();
  const position = allLessons.findIndex((item) => item.id === id);
  const next = allLessons[position + 1];
  const score = progress.quizScores?.[lesson.id];
  elements.lessonDetail.innerHTML = `<div class="lesson-detail-top"><span class="level-pill">${lesson.level}</span><a class="text-button" href="#learning-path">Back to path</a></div><h2 id="lesson-detail-heading">${lesson.title}</h2><p class="lesson-outcome">${lesson.description}</p><div class="lesson-facts"><span>${lesson.minutes} minutes</span>${lesson.technologies.map((item) => `<span>${item}</span>`).join("")}${score !== undefined ? `<span class="score-badge">Checkpoint score ${score}%</span>` : ""}</div><div class="lesson-actions"><a class="primary-button" href="${lesson.material}">Read theory and best practices</a><a class="secondary-button" href="${lesson.notebook}">Run guided notebook</a><a class="secondary-button" href="#quiz-${lesson.id}">Take checkpoint quiz</a></div><p class="lesson-tip">Study the theory, run the notebook, complete the exercise, then use the quiz checkpoint to test your understanding.</p>${next ? `<a class="next-lesson" href="#lesson-${next.id}">Next: ${next.title} →</a>` : `<p class="next-lesson">You reached the end of the learning path.</p>`}`;
  elements.lessonDetail.hidden = false;
  elements.lessonDetail.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderQuestions() {
  let previousCategory = null;
  const visibleQuestions = activeQuestions();

  elements.questionList.innerHTML = visibleQuestions
    .map((question, questionIndex) => {
      const selected = new Set(selections[question.id] ?? []);
      const categoryAnchor =
        question.category !== previousCategory
          ? `id="category-${categorySlug(question.category)}"`
          : "";
      previousCategory = question.category;

      const options = question.options
        .map(
          (option, optionIndex) => `
            <label class="option" data-option-index="${optionIndex}">
              <input
                type="checkbox"
                name="${question.id}"
                value="${optionIndex}"
                ${selected.has(optionIndex) ? "checked" : ""}
              />
              <span>${option}</span>
            </label>
          `,
        )
        .join("");

      return `
        <article class="question-card" data-question-id="${question.id}" ${categoryAnchor}>
          <div class="question-meta">
            <div>
              <span class="category-pill">${question.category}</span>
              <span class="question-number">Question ${questionIndex + 1}</span>
            </div>
            <span class="answer-status" hidden></span>
          </div>
          <fieldset>
            <legend>${question.prompt}</legend>
            <div class="option-list">${options}</div>
          </fieldset>
          <div class="review-panel" hidden>
            <h3>Correct answer</h3>
            <p class="correct-answer-copy"></p>
            <p>${question.explanation}</p>
            <p>
              <a href="${repositoryContentBase}${question.source.url}">
                Review: ${question.source.label}
              </a>
            </p>
          </div>
        </article>
      `;
    })
    .join("");
}

function updateProgress() {
  const answered = answeredTotal();
  const total = activeQuestions().length;
  elements.answeredCount.textContent = answered;
  elements.progressTrack.max = total;
  elements.progressTrack.value = answered;
  elements.progressTrack.textContent = `${answered} of ${total} answered`;
}

function clearGradePresentation() {
  latestGrade = null;
  showingReview = false;
  elements.results.hidden = true;

  document.querySelectorAll(".question-card").forEach((card) => {
    card.classList.remove("is-correct", "is-incorrect");
    card.querySelector(".answer-status").hidden = true;
    card.querySelector(".review-panel").hidden = true;
    card.querySelectorAll(".option").forEach((option) => {
      option.classList.remove("is-answer", "is-selected-wrong");
    });
  });
}

function renderGrade() {
  latestGrade = gradeQuiz(activeQuestions(), selections);
  const checkpointId = window.location.hash.replace(/^#quiz-/, "");
  if (allLessons.some((lesson) => lesson.id === checkpointId)) { progress.quizScores = { ...(progress.quizScores ?? {}), [checkpointId]: latestGrade.percent }; saveProgress(); }
  showingReview = false;

  elements.results.hidden = false;
  elements.scorePercent.textContent = `${latestGrade.percent}%`;
  elements.results.style.setProperty(
    "--score-angle",
    `${latestGrade.percent * 3.6}deg`,
  );
  elements.scoreHeading.textContent =
    latestGrade.percent >= 85
      ? "Strong RAG understanding"
      : latestGrade.percent >= 65
        ? "Solid foundation—keep refining"
        : "Good start—review the explanations";
  elements.scoreSummary.textContent =
    `You answered ${latestGrade.correctCount} of ${latestGrade.total} questions correctly ` +
    `and completed ${latestGrade.answeredCount} of ${latestGrade.total}.`;
  elements.reviewButton.textContent = "View correct answers";

  elements.topicScores.innerHTML = Object.entries(latestGrade.categories)
    .map(
      ([category, score]) => `
        <li class="topic-score">
          <span>${category}</span>
          <strong>${score.correct}/${score.total}</strong>
        </li>
      `,
    )
    .join("");

  latestGrade.details.forEach((detail) => {
    const card = document.querySelector(`[data-question-id="${detail.id}"]`);
    const status = card.querySelector(".answer-status");
    card.classList.toggle("is-correct", detail.correct);
    card.classList.toggle("is-incorrect", !detail.correct);
    status.hidden = false;
    status.className = `answer-status ${detail.correct ? "correct" : "incorrect"}`;
    status.textContent = detail.correct ? "Correct" : "Needs review";
  });

  elements.results.scrollIntoView({ behavior: "smooth", block: "center" });
}

function toggleReview() {
  if (!latestGrade) return;
  showingReview = !showingReview;
  elements.reviewButton.textContent = showingReview
    ? "Hide correct answers"
    : "View correct answers";

  questions.forEach((question) => {
    const card = document.querySelector(`[data-question-id="${question.id}"]`);
    const reviewPanel = card.querySelector(".review-panel");
    const selected = new Set(selections[question.id] ?? []);
    reviewPanel.hidden = !showingReview;
    card.querySelector(".correct-answer-copy").textContent = question.correct
      .map((index) => question.options[index])
      .join(" • ");

    card.querySelectorAll(".option").forEach((option, optionIndex) => {
      option.classList.toggle(
        "is-answer",
        showingReview && question.correct.includes(optionIndex),
      );
      option.classList.toggle(
        "is-selected-wrong",
        showingReview &&
          selected.has(optionIndex) &&
          !question.correct.includes(optionIndex),
      );
    });
  });
}

elements.form.addEventListener("change", (event) => {
  const checkbox = event.target;
  if (!(checkbox instanceof HTMLInputElement) || checkbox.type !== "checkbox") {
    return;
  }

  selections[checkbox.name] = [
    ...elements.form.querySelectorAll(`input[name="${checkbox.name}"]:checked`),
  ].map((input) => Number(input.value));

  saveSelections();
  updateProgress();
  clearGradePresentation();
});

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  renderGrade();
});

elements.reviewButton.addEventListener("click", toggleReview);

elements.retryButton.addEventListener("click", () => {
  showingReview = false;
  elements.results.hidden = true;
  document.querySelector("#quiz-heading").scrollIntoView({ behavior: "smooth" });
});

elements.resetButton.addEventListener("click", () => {
  if (!window.confirm("Clear every selected answer and score?")) return;

  selections = {};
  saveSelections();
  renderQuestions();
  updateProgress();
  clearGradePresentation();
});

elements.questionCount.textContent = questions.length;
elements.progressTotal.textContent = activeQuestions().length;
renderCategoryList();
renderLearningPath();
bindLearningActions();
elements.levelFilter.addEventListener("change", () => { renderLearningPath(); bindLearningActions(); });
elements.lessonFilter.addEventListener("input", () => { renderLearningPath(); bindLearningActions(); });
elements.clearFilters.addEventListener("click", () => { elements.levelFilter.value = "all"; elements.lessonFilter.value = ""; renderLearningPath(); bindLearningActions(); });
renderQuestions();
updateProgress();
window.addEventListener("hashchange", () => {
  renderCategoryList();
  renderQuestions();
  updateProgress();
  elements.questionCount.textContent = activeQuestions().length;
  elements.progressTotal.textContent = activeQuestions().length;
  showLessonFromHash();
});
showLessonFromHash();
