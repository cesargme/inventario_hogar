/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#8B4513',
        secondary: '#6B8E23',
        beige: '#F5F5DC',
        'brown-dark': '#2C1810',
      },
    },
  },
  plugins: [],
}
