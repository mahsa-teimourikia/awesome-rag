import { cp, mkdir } from "node:fs/promises";

await mkdir("out/quiz", { recursive: true });
await cp("quiz", "out/quiz", {
  recursive: true,
  filter: (source) => !source.includes("node_modules") && !source.endsWith("package-lock.json"),
});

console.log("Copied quiz page to out/quiz.");
