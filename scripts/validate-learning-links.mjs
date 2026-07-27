import { access, readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const page = await readFile(resolve(root, "app/page.tsx"), "utf8");
const paths = [...page.matchAll(/(?:notebook|example):"([^"]+)"/g)].map((match) => match[1]);
const guideBlock = page.match(/const guidePaths[^=]*=\{([\s\S]*?)\n\};/);
if (guideBlock) paths.push(...[...guideBlock[1].matchAll(/:"([^"]+)"/g)].map((match) => match[1]));

const uniquePaths = [...new Set(paths)];
for (const path of uniquePaths) {
  if (/^https?:\/\//.test(path)) continue;
  try {
    await access(resolve(root, path));
  } catch {
    throw new Error(`Learning Hub link does not exist: ${path}`);
  }
}
console.log(`Validated ${uniquePaths.length} learning material links.`);
