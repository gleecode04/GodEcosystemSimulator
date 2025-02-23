import React from "react";
import { motion } from "framer-motion";
import "./input.css";

const Mission = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <section id="how-it-works" className="how-it-works">
      <h2>How It Works</h2>
      <p>🌱 Choose an environment and set initial conditions.</p>
      <p>🔧 Adjust environmental factors like temperature, pollution, and species diversity.</p>
      <p>📊 Observe real-time simulations and adaptive data visualizations.</p>
      <p>🎯 Complete random goals or activate "God Mode" for ultimate control.</p>
    </section>
    </motion.div>

    
  );
};

export default Mission;