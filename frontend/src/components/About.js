import React from "react";
import { motion } from "framer-motion";
import "./input.css";


const About = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <section id="about" className="about">
        <h2 style={{color: "white"}}>About EcoSim</h2>
        <p style={{color: "white"}}>
          EcoSim is designed to educate and engage users on environmental changes by 
          allowing them to manipulate variables and observe their effects.
        </p>
      </section>
    </motion.div>
  );
};

export default About;