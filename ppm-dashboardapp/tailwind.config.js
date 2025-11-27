/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./html/**/*.html",
    "./js/**/*.js",
    "./config/**/*.js",
    "./index.html"
  ],
  theme: {
    extend: {
      colors: {
        // 企業ブランドカラー
        "kkc-orange": "#FF7600",
        "kkc-orange-light": "#FF8F33",
        "kkc-orange-dark": "#CC5F00",
        
        // 言語切替時のグラデーションカラー
        "gradient-start": "#667eea",
        "gradient-end": "#764ba2"
      }
    },
  },
  plugins: [],
}