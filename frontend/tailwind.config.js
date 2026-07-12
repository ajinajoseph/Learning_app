/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#F0F2FF',
          100: '#E0E4FF',
          200: '#C1C7FF',
          300: '#9EA7FF',
          400: '#7A84FC',
          500: '#4F46E5', // Indigo
          600: '#3F35C6',
          700: '#2E259F',
          800: '#201A79',
          950: '#0F0B46'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
