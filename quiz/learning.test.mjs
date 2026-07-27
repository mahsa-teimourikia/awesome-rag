import test from "node:test";
import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { allLessons, learningPath } from "./learning.js";
import { questions } from "./questions.js";

const quizDirectory = dirname(fileURLToPath(import.meta.url));

test("learning registry has three levels and complete lesson metadata", () => {
  assert.deepEqual(learningPath.map((track) => track.level), ["Beginner", "Intermediate", "Advanced"]);
  assert.ok(allLessons.length >= 15);
  for (const lesson of allLessons) {
    assert.ok(lesson.id && lesson.material && lesson.notebook && lesson.category);
    assert.ok(lesson.minutes > 0 && lesson.technologies.length > 0);
  }
});

test("lesson IDs are unique and each level has a capstone or operations step", () => {
  assert.equal(new Set(allLessons.map((lesson) => lesson.id)).size, allLessons.length);
  assert.ok(allLessons.some((lesson) => lesson.id === "beginner-capstone"));
  assert.ok(allLessons.some((lesson) => lesson.id === "advanced-operations"));
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
  for (const lesson of allLessons) {
    assert.ok(categories.has(lesson.category), `${lesson.id} uses unknown quiz category: ${lesson.category}`);
  }
});
