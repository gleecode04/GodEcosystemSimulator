import React from "react";
import "./input.css";

const Footer = () => {
  return (
    <footer className="footer">
      <p>© {new Date().getFullYear()} EcoSim. All rights reserved.</p>
    </footer>
  );
};

export default Footer;
