import { access, readFile } from "node:fs/promises";
import { constants } from "node:fs";

const html = await readFile("out/index.html", "utf8");
const quizHtml = await readFile("out/quiz/index.html", "utf8");
await readFile("out/assets/one-plus-i.png");
const assets = [...html.matchAll(/(?:src|href)="(\/awesome-rag\/assets\/[^"?]+)"/g)].map(([, path]) => path);
if (!assets.length) throw new Error("No hashed Pages assets found");
for (const asset of assets) await access(`out/${asset.replace(/^\/awesome-rag\//, "")}`, constants.R_OK);
const javascript = await Promise.all(assets.filter((asset) => asset.endsWith(".js")).map((asset) => readFile(`out/${asset.replace(/^\/awesome-rag\//, "")}`, "utf8")));
const bundle = javascript.join("\n");
if (!bundle.includes("Build answers") || !bundle.includes("FIELD GUIDE") || !bundle.includes("Corrective RAG") || !bundle.includes("Adaptive RAG") || !bundle.includes("Enterprise RAG Platform Capstone")) throw new Error("Pages bundle is missing current Field Guide learning content");
if (!quizHtml.includes("RAG KNOWLEDGE CHECK") || !quizHtml.includes("question-list")) throw new Error("Quiz page artifact is missing the knowledge check shell");
if (quizHtml.includes("/LEARNING.md")) throw new Error("Quiz page links to the removed LEARNING.md guide");
console.log(`Pages smoke check passed (${assets.length} assets, Field Guide bundle, quiz page, and One+i branding present).`);
