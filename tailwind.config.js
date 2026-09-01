/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './dashboard/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        // Sanish pastel-luxury palette
        surface: {
          50:  '#FBF8F5',
          100: '#F6F1F8',
          200: '#F4EDF7',
          300: '#EFE7F3',
        },
        dark: {
          900: '#1A1822',
          800: '#23202E',
          700: '#2E2A3A',
          600: '#3A3548',
        },
        accent: {
          DEFAULT: '#8EA9C4',
          hover:   '#7a98b5',
          light:   '#B8CDD9',
          muted:   '#D4E2EC',
        },
      },
      borderRadius: {
        '2xl':  '18px',
        '3xl':  '22px',
        '4xl':  '28px',
        'pill': '999px',
      },
      boxShadow: {
        'card':   '0 2px 20px rgba(0,0,0,0.06)',
        'card-md':'0 4px 32px rgba(0,0,0,0.10)',
        'glow':   '0 0 0 3px rgba(142,169,196,0.25)',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
