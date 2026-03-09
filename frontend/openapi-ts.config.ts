import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "http://localhost:8000/openapi.json",
  output: { entryFile: false, path: "src/lib/openapi" },
  plugins: ["@hey-api/typescript"],
});
