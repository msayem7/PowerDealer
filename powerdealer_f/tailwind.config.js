/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1976d2',
          dark: '#1565c0',
          light: '#e3f2fd',
        },
        surface: '#ffffff',
        background: '#f5f5f5',
      },
      spacing: {
        'header-height': '64px',
        'sidebar-expanded': '240px',
        'sidebar-collapsed': '64px',
      },
    },
  },
  plugins: [],
}
