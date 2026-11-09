/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#231c19",
        sage: "#ffedd5",
        moss: "#ea580c"
      },
      boxShadow: {
        soft: "0 12px 40px rgba(154, 52, 18, .09)"
      }
    }
  },
  plugins: []
};
