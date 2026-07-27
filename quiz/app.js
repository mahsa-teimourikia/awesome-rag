import { gradeQuiz } from "./grading.js";
import { questions } from "./questions.js";
import { learningPath } from "./learning.js";

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

function answeredTotal() {
  return questions.filter((question) => (selections[question.id] ?? []).length > 0)
    .length;
}

function categorySlug(category) {
  return category.toLowerCase().replaceAll(/\s+/g, "-");
}

function renderCategoryList() {
  const counts = questions.reduce((result, question) => {
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
  elements.learningPathList.innerHTML = learningPath.map((track) => `
    <section class="learning-track ${track.tone}">
      <div class="track-heading"><div><span class="level-pill">${track.level}</span><h3>${track.outcome}</h3></div><span class="track-count">${track.modules.length} steps</span></div>
      <ol class="learning-modules">${track.modules.map(([title, description, material, notebook, category], index) => `
        <li class="learning-module"><span class="module-number">${index + 1}</span><div><h4>${title}</h4><p>${description}</p><div class="module-links"><a href="${material}">Read lesson</a><a href="${notebook}">Open notebook</a><a href="#category-${categorySlug(category)}">Quiz: ${category}</a></div></div></li>
      `).join("")}</ol>
    </section>
  `).join("");
}

function renderQuestions() {
  let previousCategory = null;

  elements.questionList.innerHTML = questions
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
  const total = questions.length;
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
  latestGrade = gradeQuiz(questions, selections);
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
elements.progressTotal.textContent = questions.length;
renderCategoryList();
renderLearningPath();
renderQuestions();
updateProgress();
