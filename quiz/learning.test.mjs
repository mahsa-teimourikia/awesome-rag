import test from "node:test";
import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { allLessons, learningPath } from "./learning.js";
import { questions } from "./questions.js";
import { lessonContent } from "./content.js";

const quizDirectory = dirname(fileURLToPath(import.meta.url));

test("learning registry has three levels and complete lesson metadata", () => {
  assert.deepEqual(learningPath.map((track) => track.level), ["Beginner", "Intermediate", "Advanced"]);
  assert.ok(allLessons.length >= 15);
  for (const lesson of allLessons) {
    assert.ok(lesson.id && lesson.material && lesson.notebook && lesson.category);
    assert.ok(lesson.minutes > 0 && lesson.technologies.length > 0);
    assert.ok(lesson.questionIds.length > 0, `${lesson.id} should define checkpoint questions`);
  }
});

test("lesson IDs are unique and each level has a capstone or operations step", () => {
  assert.equal(new Set(allLessons.map((lesson) => lesson.id)).size, allLessons.length);
  assert.ok(allLessons.some((lesson) => lesson.id === "b5"));
  assert.ok(allLessons.some((lesson) => lesson.id === "a6"));
  assert.ok(allLessons.some((lesson) => lesson.id === "a7"));
});

test("every lesson points to a readable material file and notebook", async () => {
  for (const lesson of allLessons) {
    const materialPath = resolve(quizDirectory, lesson.material);
    const notebookPath = resolve(quizDirectory, lesson.notebook);
    await access(materialPath);
    await access(notebookPath);

    const notebook = JSON.parse(await readFile(notebookPath, "utf8"));
    assert.equal(notebook.nbformat, 4, `${lesson.id} notebook should be nbformat 4`);
    assert.ok(Array.isArray(notebook.cells) && notebook.cells.length > 0, `${lesson.id} notebook should contain cells`);
  }
});

test("lesson quiz categories map to available questions", () => {
  const categories = new Set(questions.map((question) => question.category));
  const questionIds = new Set(questions.map((question) => question.id));
  for (const lesson of allLessons) {
    assert.ok(categories.has(lesson.category), `${lesson.id} uses unknown quiz category: ${lesson.category}`);
    assert.equal(new Set(lesson.questionIds).size, lesson.questionIds.length);
    for (const questionId of lesson.questionIds) assert.ok(questionIds.has(questionId), `${lesson.id} uses unknown question: ${questionId}`);
  }
});

test("every lesson category has self-contained hub content and references", () => {
  for (const lesson of allLessons) {
    const content = lessonContent[lesson.category];
    assert.ok(content, `${lesson.id} has no embedded learning content`);
    assert.ok(content.theory.length > 80);
    assert.ok(content.workflow.length >= 3 && content.bestPractices.length >= 3);
    assert.ok(content.references.length >= 1);
    for (const reference of content.references) {
      assert.match(reference.url, /^(?:https?:\/\/|curriculum\/)/);
    }
  }
});
