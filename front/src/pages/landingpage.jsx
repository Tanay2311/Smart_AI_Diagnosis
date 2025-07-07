import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-purple-100 to-blue-200 text-center px-4">
      <motion.h1
        className="text-4xl font-bold text-purple-800 mb-4"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        🩺 Welcome to Smart AI Medical Assistant
      </motion.h1>

      <motion.p
        className="text-lg text-gray-700 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 1 }}
      >
        Your personal health companion powered by AI
      </motion.p>

      <motion.button
        onClick={() => navigate("/demographics")}
        className="px-8 py-3 bg-purple-700 text-white text-lg rounded-lg shadow hover:bg-purple-800 transition"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Get Started
      </motion.button>
    </div>
  );
}
