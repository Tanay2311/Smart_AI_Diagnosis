import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Player } from "@lottiefiles/react-lottie-player";
import animationData from "../assets/Doctor.json";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-purple-100 to-blue-200 dark:from-gray-900 dark:to-gray-800 text-center px-4">
      
      {/* Lottie animation centered */}
      <Player
        autoplay
        loop
        src={animationData}
        style={{ height: "250px", width: "250px", marginBottom: "1rem" }}
      />

      {/* Heading */}
      <motion.h1
        className="text-4xl font-bold text-purple-800 dark:text-purple-300 mb-4"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        🩺 Welcome to Smart AI Medical Assistant
      </motion.h1>

      {/* Subheading */}
      <motion.p
        className="text-lg text-gray-700 dark:text-gray-300 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 1 }}
      >
        Your personal health companion powered by AI
      </motion.p>

      {/* Button */}
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
