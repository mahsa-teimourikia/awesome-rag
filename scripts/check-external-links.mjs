import { readFile } from "node:fs/promises";

const source = await readFile("app/page.tsx", "utf8");
const urls = [...new Set([...source.matchAll(/(https?:\/\/[^"'\s)]+)/g)].map(([, url]) => url.replace(/[),.;]+$/, "")))];
const failures = [];
for (const url of urls) {
  try {
    const response = await fetch(url, { method: "HEAD", signal: AbortSignal.timeout(10000) });
    if (response.status >= 400) failures.push(`${response.status} ${url}`);
    else console.log(`${response.status} ${url}`);
  } catch (error) {
    failures.push(`${error.message} ${url}`);
  }
}
if (failures.length) {
  console.error("External link check failed:\n" + failures.join("\n"));
  process.exitCode = 1;
}
