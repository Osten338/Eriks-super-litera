/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        diff: {
          insert: '#1e3a8a', // blue-800
          delete: '#b91c1c', // red-700
          move: '#065f46',   // emerald-800
        }
      }
    },
  },
  plugins: [],
}


