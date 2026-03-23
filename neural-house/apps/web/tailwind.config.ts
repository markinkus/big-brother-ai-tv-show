import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "../../packages/*/src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: "var(--color-surface)",
        surfaceAlt: "var(--color-surface-alt)",
        ink: "var(--color-ink)",
        accent: "var(--color-accent)",
        accentMuted: "var(--color-accent-muted)",
        grid: "var(--color-grid)",
        danger: "var(--color-danger)",
        success: "var(--color-success)",
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"],
      },
      boxShadow: {
        panel: "0 0 0 2px rgba(255,255,255,0.04), 0 12px 30px rgba(0,0,0,0.28)",
      },
    },
  },
  plugins: [],
};

export default config;
