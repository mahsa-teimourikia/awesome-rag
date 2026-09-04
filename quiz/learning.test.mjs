import test from "node:test";
import assert from "node:assert/strict";
import { access, readFile, readdir } from "node:fs/promises";
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
    assert.ok(lesson.questionIds.length >= 3, `${lesson.id} should define at least three checkpoint questions`);
    assert.ok(lesson.notebooks.length > 0, `${lesson.id} should expose its notebook sequence`);
    assert.equal(lesson.notebooks.length, lesson.notebookLabels.length);
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
    await access(materialPath);
    for (const notebookResource of lesson.notebooks) {
      const notebookPath = resolve(quizDirectory, notebookResource);
      await access(notebookPath);
      const notebook = JSON.parse(await readFile(notebookPath, "utf8"));
      assert.equal(notebook.nbformat, 4, `${lesson.id} notebook should be nbformat 4`);
      assert.ok(Array.isArray(notebook.cells) && notebook.cells.length > 0, `${lesson.id} notebook should contain cells`);
    }
    if (lesson.implementation) await access(resolve(quizDirectory, lesson.implementation));
  }
});

test("every curriculum topic and owned learning artifact is registered", async () => {
  const registeredMaterials = new Set(allLessons.map((lesson) => lesson.material.replace(/^\.\.\//, "")));
  const registeredNotebooks = new Set(allLessons.flatMap((lesson) => lesson.notebooks.map((path) => path.replace(/^\.\.\//, ""))));
  const registeredImplementations = new Set(allLessons.filter((lesson) => lesson.implementation).map((lesson) => lesson.implementation.replace(/^\.\.\//, "")));

  for (const level of ["beginner", "intermediate", "advanced"]) {
    const levelDirectory = resolve(quizDirectory, "..", "curriculum", level);
    const topics = await readdir(levelDirectory, { withFileTypes: true });
    for (const topic of topics.filter((entry) => entry.isDirectory())) {
      const prefix = `curriculum/${level}/${topic.name}`;
      assert.ok(registeredMaterials.has(`${prefix}/README.md`), `${prefix} is missing from the learning registry`);
      const files = await readdir(resolve(levelDirectory, topic.name));
      for (const file of files.filter((name) => name.endsWith(".ipynb"))) {
        assert.ok(registeredNotebooks.has(`${prefix}/${file}`), `${prefix}/${file} is not linked from the learning registry`);
      }
      for (const file of files.filter((name) => name.endsWith(".py"))) {
        assert.ok(registeredImplementations.has(`${prefix}/${file}`), `${prefix}/${file} is not linked as a reusable implementation`);
      }
    }
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

test("every quiz question is valid, explained, and source-linked", async () => {
  assert.equal(questions.length, allLessons.length * 3);
  for (const question of questions) {
    assert.ok(question.prompt.length > 20, `${question.id} needs a meaningful prompt`);
    assert.ok(question.options.length >= 3, `${question.id} needs at least three options`);
    assert.ok(question.correct.length > 0, `${question.id} needs a correct answer`);
    assert.equal(new Set(question.correct).size, question.correct.length, `${question.id} repeats a correct option`);
    for (const index of question.correct) {
      assert.ok(Number.isInteger(index) && index >= 0 && index < question.options.length, `${question.id} has an invalid correct-answer index`);
    }
    assert.ok(question.explanation.length > 60, `${question.id} needs an explanatory review`);
    assert.ok(question.source?.label && question.source?.url, `${question.id} needs a source link`);
    await access(resolve(quizDirectory, "..", question.source.url));
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
