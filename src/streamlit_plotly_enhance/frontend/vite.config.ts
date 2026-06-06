import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  build: {
    outDir: "build",
    emptyOutDir: true,
    lib: {
      entry: "./src/index.ts",
      formats: ["es"],
      fileName: "index-[hash]"
    },
    rollupOptions: {
      output: {
        assetFileNames: "style-[hash][extname]"
      }
    }
  }
});
