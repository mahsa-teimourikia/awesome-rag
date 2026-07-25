import assert from "node:assert/strict";
import test from "node:test";

import { gradeQuiz, isExactMatch, normalizeSelection } from "./grading.js";

test("normalizeSelection removes duplicates and sorts values", () => {
  assert.deepEqual(normalizeSelection([3, 1, 3, 2]), [1, 2, 3]);
});

test("isExactMatch requires every correct answer and no incorrect answers", () => {
  assert.equal(isExactMatch([2, 0], [0, 2]), true);
  assert.equal(isExactMatch([0], [0, 2]), false);
  assert.equal(isExactMatch([0, 1, 2], [0, 2]), false);
});

test("gradeQuiz calculates totals and category breakdowns", () => {
  const sampleQuestions = [
    { id: "one", category: "A", correct: [0, 2] },
    { id: "two", category: "A", correct: [1] },
    { id: "three", category: "B", correct: [0] },
  ];
  const grade = gradeQuiz(sampleQuestions, {
    one: [2, 0],
    two: [0],
  });

  assert.equal(grade.correctCount, 1);
  assert.equal(grade.answeredCount, 2);
  assert.equal(grade.total, 3);
  assert.equal(grade.percent, 33);
  assert.deepEqual(grade.categories, {
    A: { correct: 1, total: 2 },
    B: { correct: 0, total: 1 },
  });
});
