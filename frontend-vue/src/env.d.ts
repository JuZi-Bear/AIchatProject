/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_MODE?: "python" | "java";
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_PYTHON_API_BASE_URL?: string;
  readonly VITE_JAVA_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
