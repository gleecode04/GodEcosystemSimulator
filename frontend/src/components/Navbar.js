import React from "react";
import "./Navbar.css";
import { Link, useNavigate } from "react-router-dom";

const Navbar = () => {
  const navigate = useNavigate();

  return (
    <nav className="navbar">
      <h1 className="logo">ECOSIM</h1>
      <button className="launch-button" onClick={() => navigate("/simulator")}>Launch</button>
    </nav>
  );
};

export default Navbar;