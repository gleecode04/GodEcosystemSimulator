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
        <h1>Welcome to EcoSim</h1>
        <p>
          An interactive, gamified environmental simulation tool that lets you explore 
          the impact of ecological changes.
        </p>
      </header>
      <button className="launch-button" onClick={() => navigate("/simulator")}>
          Launch
        </button>
    </motion.div>
  );
};

export default Hero;