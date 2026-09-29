import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./views/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        institutional: {
          navy: "#062B6F",
          blue: "#1F66B8",
          deep: "#082B63",
          light: "#EAF3FC",
          green: "#198754",
          gold: "#E5A33D",
          border: "#E5E7EB",
        },
        forensic: {
          bg: "#070F1E",
          card: "#0D1B2A",
          cardHover: "#112238",
          border: "#1E2E4A",
          cyan: "#00F0FF",
          amber: "#FFB020",
          emerald: "#00E676",
          purple: "#B388FF",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Work Sans", "Noto Sans", "sans-serif"],
        display: ["var(--font-display)", "Space Grotesk", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
