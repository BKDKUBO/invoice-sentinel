import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: "#f0f4f8",
          100: "#d9e2ec",
          200: "#bcccdc",
          300: "#9fb3c8",
          400: "#829ab1",
          500: "#627d98",
          600: "#486581",
          700: "#334e68",
          800: "#243b53",
          900: "#102a43",
          950: "#0b1c2c",
        },
        gold: {
          50: "#fdf8e8",
          100: "#faefc5",
          200: "#f5df8b",
          300: "#efcb4f",
          400: "#e6b422",
          500: "#c99a12",
          600: "#a1780c",
          700: "#7a5a0e",
          800: "#5c4410",
          900: "#3f2f0c",
        },
        ph: { blue: "#0038a8", red: "#ce1126", gold: "#fcd116" },
      },
      fontFamily: {
        sans: ["\"Inter Variable\"", "Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Arial", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
