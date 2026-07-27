import test from "node:test";
import assert from "node:assert/strict";
import { allLessons, learningPath } from "./learning.js";

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
