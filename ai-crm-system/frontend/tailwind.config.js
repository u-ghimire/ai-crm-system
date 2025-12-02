// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class', // Enable dark mode with class strategy
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          primary: {
            50: '#e6f2ff',
            100: '#cce5ff',
            200: '#99cbff',
            300: '#66b0ff',
            400: '#3396ff',
            500: '#007bff',
            600: '#0062cc',
            700: '#004a99',
            800: '#003166',
            900: '#001933',
          },
          accent: {
            50: '#fff4e6',
            100: '#ffe9cc',
            200: '#ffd399',
            300: '#ffbd66',
            400: '#ffa733',
            500: '#ff9100',
            600: '#cc7400',
            700: '#995700',
            800: '#663a00',
            900: '#331d00',
          },
          success: {
            50: '#e8f5e9',
            100: '#c8e6c9',
            200: '#a5d6a7',
            300: '#81c784',
            400: '#66bb6a',
            500: '#4caf50',
            600: '#43a047',
            700: '#388e3c',
            800: '#2e7d32',
            900: '#1b5e20',
          },
          danger: {
            50: '#ffebee',
            100: '#ffcdd2',
            200: '#ef9a9a',
            300: '#e57373',
            400: '#ef5350',
            500: '#f44336',
            600: '#e53935',
            700: '#d32f2f',
            800: '#c62828',
            900: '#b71c1c',
          },
          warning: {
            50: '#fff8e1',
            100: '#ffecb3',
            200: '#ffe082',
            300: '#ffd54f',
            400: '#ffca28',
            500: '#ffc107',
            600: '#ffb300',
            700: '#ffa000',
            800: '#ff8f00',
            900: '#ff6f00',
          },
        },
        animation: {
          'slide-up': 'slideUp 0.3s ease-out',
          'slide-down': 'slideDown 0.3s ease-out',
          'fade-in': 'fadeIn 0.3s ease-out',
        },
        keyframes: {
          slideUp: {
            '0%': { transform: 'translateY(100%)' },
            '100%': { transform: 'translateY(0)' },
          },
          slideDown: {
            '0%': { transform: 'translateY(-100%)' },
            '100%': { transform: 'translateY(0)' },
          },
          fadeIn: {
            '0%': { opacity: '0' },
            '100%': { opacity: '1' },
          },
        },
      },
    },
    plugins: [],
  }