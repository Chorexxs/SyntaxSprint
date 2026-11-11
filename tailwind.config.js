/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./syntax_sprint/templates/**/*.html",
    "./syntax_sprint/static/js/**/*.js",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "bg-primary": "var(--bg-primary)",
        "bg-secondary": "var(--bg-secondary)",
        "text-main": "var(--text-main)",
        "text-sub": "var(--text-sub)",
        "text-active": "var(--text-active)",
        caret: "var(--caret)",
        success: "var(--success)",
        error: "var(--error)",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
    },
  },
  plugins: [],
};
