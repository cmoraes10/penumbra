import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // paleta da penumbra, do claro ao mais fundo na sombra
        penumbra: {
          bg: "#0f1117",
          card: "#171a22",
          borda: "#252a36",
          texto: "#e7e9ee",
          suave: "#9aa3b2",
          destaque: "#e8a838",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
