export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#F4F2FC",
        sidebar: "#FFFFFF",
        card: "#FFFFFF",
        elevated: "#F8F7FD",
        border: "#E3DEF5",
        textPrimary: "#0F1222",
        textSecondary: "#1F2233",
        textMuted: "#3A3D52",
        purple: "#6C4EE3",
        pink: "#FF6FA5",
        yellow: "#FFC93C",
        blue: "#2F8FFF",
        statPurple: "#DDD3FB",
        statYellow: "#FDE68A",
        statPink: "#FFD1E8",
        statBlue: "#BFE0FF",
        success: "#16A34A",
        warning: "#D97706",
        danger: "#E0355B",
      },
      fontFamily: {
        sans: ["Lato", "system-ui", "sans-serif"],
        heading: ["Space Grotesk", "system-ui", "sans-serif"],
      },
      borderRadius: { xl2: "20px" },
    },
  },
  plugins: [],
};
