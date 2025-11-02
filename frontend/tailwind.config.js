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
        },
        ink: '#080A12',
        surface: '#151A2F',
        accent: '#79FFA8',
      },
      backgroundImage: {
        'grad-primary': 'linear-gradient(135deg, #5B3DF5 0%, #2AC7FF 100%)',
        'grad-accent': 'linear-gradient(135deg, #2AC7FF 0%, #79FFA8 100%)',
      },
      boxShadow: {
        glow: '0 0 40px 6px rgba(90, 80, 255, 0.25)',
        'glow-sm': '0 0 24px 4px rgba(90, 80, 255, 0.2)',
      },
      borderRadius: {
        xl: '14px',
        '2xl': '20px',
      },
      keyframes: {
        aurora: {
          '0%, 100%': { transform: 'translateY(-10%)' },
          '50%': { transform: 'translateY(10%)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
      },
      animation: {
        aurora: 'aurora 18s ease-in-out infinite',
        float: 'float 6s ease-in-out infinite',
        shimmer: 'shimmer 1.6s linear infinite',
      },
    },
  },
  plugins: [],
}


