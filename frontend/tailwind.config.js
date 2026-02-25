export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: "#0f2440",
          deep: "#0a1628",
          light: "#0d3a52",
        },
        surface: {
          primary: "#F4F6F8",
          secondary: "#E6EBF0",
        },
        accent: {
          DEFAULT: "#F59E0B",
          hover: "#D97706",
        },
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        fadeIn: 'fadeIn 0.6s ease-out',
      },
    },
  },
  plugins: [],
};
