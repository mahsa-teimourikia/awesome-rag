export function normalizeSelection(selection = []) {
  return [...new Set(selection)].map(Number).sort((a, b) => a - b);
}

export function isExactMatch(selection, correct) {
  const selected = normalizeSelection(selection);
  const expected = normalizeSelection(correct);

  return (
    selected.length === expected.length &&
    selected.every((value, index) => value === expected[index])
  );
}

export function gradeQuiz(questions, selections = {}) {
  const categories = {};
  let correctCount = 0;
  let answeredCount = 0;

  const details = questions.map((question) => {
    const selected = normalizeSelection(selections[question.id] ?? []);
    const correct = isExactMatch(selected, question.correct);

    if (selected.length > 0) answeredCount += 1;
    if (correct) correctCount += 1;

    categories[question.category] ??= { correct: 0, total: 0 };
    categories[question.category].total += 1;
    if (correct) categories[question.category].correct += 1;

    return {
      id: question.id,
      selected,
      correct,
    };
  });

  return {
    answeredCount,
    correctCount,
    total: questions.length,
    percent: questions.length
      ? Math.round((correctCount / questions.length) * 100)
      : 0,
    categories,
    details,
  };
}
