import { describe, expect, it } from "vitest";
import { readdirSync, readFileSync, statSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const srcDir = dirname(fileURLToPath(import.meta.url));

const sourceFiles = (dir) =>
  readdirSync(dir).flatMap((entry) => {
    const path = join(dir, entry);

    if (entry === "__generated__") {
      return [];
    }
    if (statSync(path).isDirectory()) {
      return sourceFiles(path);
    }
    return /\.(js|jsx)$/.test(entry) && !/\.test\.(js|jsx)$/.test(entry)
      ? [path]
      : [];
  });

describe("frontend GraphQL defaults", () => {
  it("does not default MainProject variables to operational project names", () => {
    const source = sourceFiles(srcDir)
      .map((path) => readFileSync(path, "utf8"))
      .join("\n");

    expect(source).not.toContain('defaultValue: "MeerTIME"');
  });
});
