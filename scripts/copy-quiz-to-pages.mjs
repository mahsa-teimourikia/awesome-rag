import { cp, mkdir } from "node:fs/promises";

await mkdir("out/quiz", { recursive: true });
await mkdir("out/assets", { recursive: true });
await cp("quiz", "out/quiz", {
  recursive: true,
  filter: (source) => !source.includes("node_modules") && !source.endsWith("package-lock.json"),
});
await cp("assets/one-plus-i.png", "out/assets/one-plus-i.png");

console.log("Copied quiz page and One+i branding asset to Pages output.");
