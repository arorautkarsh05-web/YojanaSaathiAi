/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#17251F',
          900: '#1D3028',
          800: '#2A4339',
        },
        forest: {
          800: '#244C3B',
          700: '#2D5E49',
          900: '#1A372B',
        },
        leaf: {
          600: '#4E7957',
          500: '#5F8E69',
          700: '#3D6045',
        },
        field: {
          100: '#E8EFE4',
          50: '#F3F7F0',
          200: '#D5E2CE',
        },
        paper: {
          50: '#F8F7F1',
          100: '#F0EFE7',
          200: '#E4E2D5',
        },
        earth: {
          500: '#A56E43',
          600: '#8A5934',
          400: '#BA8051',
        },
        sun: {
          400: '#E4B85C',
          500: '#D4A33B',
          300: '#ECC779',
        },
        muted: {
          DEFAULT: '#66736B',
          dark: '#4C5851',
          light: '#85938B',
        },
        appBorder: '#DDE2D8',
        brandSuccess: '#28734D',
        brandWarning: '#95621C',
        brandDanger: '#A33D35',
        brandInfo: '#315F83',
      },
      fontFamily: {
        serif: ['Fraunces', 'DM Serif Display', 'serif'],
        sans: ['Inter', 'Noto Sans Devanagari', 'system-ui', 'sans-serif'],
        hindi: ['Noto Sans Devanagari', 'Inter', 'sans-serif'],
      },
      borderRadius: {
        'natural': '6px',
        'subtle': '8px',
        'panel': '12px',
      },
    },
  },
  plugins: [],
}

