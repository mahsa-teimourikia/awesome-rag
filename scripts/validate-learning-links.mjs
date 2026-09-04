import { access, readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const page = await readFile(resolve(root, "app/page.tsx"), "utf8");
const quizIndex = await readFile(resolve(root, "quiz/index.html"), "utf8");
const quizLearning = await readFile(resolve(root, "quiz/learning.js"), "utf8");
const quizContent = await readFile(resolve(root, "quiz/content.js"), "utf8");
const quizQuestions = await readFile(resolve(root, "quiz/questions.js"), "utf8");
const learningSources = [page, quizIndex, quizLearning, quizContent, quizQuestions];
const paths = [...page.matchAll(/(?:notebook|example):"([^"]+)"/g)].map((match) => match[1]);
const guideBlock = page.match(/const guidePaths[^=]*=\{([\s\S]*?)\n\};/);
if (guideBlock) paths.push(...[...guideBlock[1].matchAll(/:"([^"]+)"/g)].map((match) => match[1]));

// The Hub also exposes local curriculum and source references in `refs` arrays.
// Extract all local source-like paths from the registry so a card cannot point
// learners at an in-repository resource that was renamed or removed.
const localReferencePattern = /curriculum\/[A-Za-z0-9_./-]+\.(?:md|ipynb|py)(?:#[A-Za-z0-9_-]+)?/g;
for (const source of learningSources) {
  paths.push(...[...source.matchAll(localReferencePattern)].map((match) => match[0].split("#")[0]));
}

const repositoryBlobPattern = /https:\/\/github\.com\/mahsa-teimourikia\/awesome-rag\/blob\/main\/([^"#?]+)/g;
paths.push(...[...quizIndex.matchAll(repositoryBlobPattern)].map((match) => match[1]));

const uniquePaths = [...new Set(paths)];
for (const path of uniquePaths) {
  if (/^https?:\/\//.test(path)) continue;
  const normalizedPath = path.replace(/^(\.\.\/)+/, "");
  try {
    await access(resolve(root, normalizedPath));
  } catch {
    throw new Error(`Learning Hub or quiz link does not exist: ${normalizedPath}`);
  }
}
console.log(`Validated ${uniquePaths.length} Learning Hub and quiz links.`);
