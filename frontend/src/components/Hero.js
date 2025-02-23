import React from "react";
import { motion } from "framer-motion";
import "./input.css";
import { useNavigate } from "react-router-dom";

const Hero = () => {
  const navigate = useNavigate();
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <header id="hero" className="hero">
        <h1>Ecosystem Simulator Game</h1>
        <button className="launch-button" onClick={() => navigate("/simulator")}>
          LAUNCH
        </button>
      </header>
    </motion.div>
  );
};

export default Hero;