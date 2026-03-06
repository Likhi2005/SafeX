/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F19',
        card: '#111827',
        border: '#1F2937',
        primary: '#06B6D4',
        secondary: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
        textPrimary: '#E5E7EB',
        textMuted: '#9CA3AF',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(6, 182, 212, 0.3)',
        'glow-green': '0 0 20px rgba(34, 197, 94, 0.3)',
        'glow-red': '0 0 20px rgba(239, 68, 68, 0.3)',
        'glow-yellow': '0 0 20px rgba(245, 158, 11, 0.3)',
      }
    },
  },
  plugins: [],
}

