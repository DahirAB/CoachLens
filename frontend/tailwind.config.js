export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0B1C2D", // navy 
        surface: { // cards
          primary: "#F4F6F8",
          secondary: "#E6EBF0",
        }
      },
    },
  },
  plugins: [],
};
