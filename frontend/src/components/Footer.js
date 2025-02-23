import React from "react";
import { motion } from "framer-motion";
import "./input.css";

const Footer = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
    <footer className="footer">
      <p>© {new Date().getFullYear()} EcoSim. All rights reserved.</p>
    </footer>
    </motion.div>
   
  );
};

export default Footer;