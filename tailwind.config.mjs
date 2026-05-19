/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          50:  '#f6f7f9',
          100: '#eceef2',
          200: '#d3d8e0',
          300: '#aab2c0',
          400: '#7a8395',
          500: '#525c70',
          600: '#3a4358',
          700: '#2a3145',
          800: '#1d2235',
          900: '#11142a',
        },
        accent: {
          DEFAULT: '#5b8cff',
          dark: '#3d6ee0',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            'h1, h2, h3, h4': { fontWeight: '600' },
            a: { textDecoration: 'none', borderBottom: '1px solid currentColor' },
          },
        },
      },
    },
  },
  plugins: [],
};
