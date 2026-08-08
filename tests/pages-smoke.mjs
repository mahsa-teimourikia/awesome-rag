import { access, readFile } from "node:fs/promises";
import { constants } from "node:fs";

const html = await readFile("out/index.html", "utf8");
const quizHtml = await readFile("out/quiz/index.html", "utf8");
const assets = [...html.matchAll(/(?:src|href)="(\/awsome-rag\/assets\/[^"?]+)"/g)].map(([, path]) => path);
if (!assets.length) throw new Error("No hashed Pages assets found");
for (const asset of assets) await access(`out/${asset.replace(/^\/awsome-rag\//, "")}`, constants.R_OK);
const javascript = await Promise.all(assets.filter((asset) => asset.endsWith(".js")).map((asset) => readFile(`out/${asset.replace(/^\/awsome-rag\//, "")}`, "utf8")));
const bundle = javascript.join("\n");
if (!bundle.includes("Build answers") || !bundle.includes("FIELD GUIDE")) throw new Error("Pages bundle is missing the Field Guide content");
if (!quizHtml.includes("Initial knowledge check") || !quizHtml.includes("question-list")) throw new Error("Quiz page artifact is missing the knowledge check shell");
console.log(`Pages smoke check passed (${assets.length} assets, Field Guide bundle and quiz page present).`);
