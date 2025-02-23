import React, { useState, useEffect } from "react";
import "./Navbar.css";
import { useNavigate } from "react-router-dom";
import { Link, Events, scrollSpy } from "react-scroll";

const Navbar = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('hero');

  useEffect(() => {
    // Initialize scrollspy
    scrollSpy.update();

    // Set up scroll event listeners
    Events.scrollEvent.register('begin', (to) => {
      setActiveSection(to);
    });

    Events.scrollEvent.register('end', (to) => {
      setActiveSection(to);
    });

    // Clean up event listeners
    return () => {
      Events.scrollEvent.remove('begin');
      Events.scrollEvent.remove('end');
    };
  }, []);

  return (
    <nav className="navbar">
      <h1 className="logo">ECOSIM</h1>
      <div className="nav-links">
        <Link
          activeClass="active"
          to="hero-section"
          spy={true}
          smooth={true}
          offset={0}
          duration={800}
          className={`nav-link ${activeSection === 'hero-section' ? 'active' : ''}`}
          containerId="main-container"
        >
          Home
        </Link>
        <Link
          activeClass="active"
          to="about-section"
          spy={true}
          smooth={true}
          offset={0}
          duration={800}
          className={`nav-link ${activeSection === 'about-section' ? 'active' : ''}`}
          containerId="main-container"
        >
          About
        </Link>
        <Link
          activeClass="active"
          to="mission-section"
          spy={true}
          smooth={true}
          offset={0}
          duration={800}
          className={`nav-link ${activeSection === 'mission-section' ? 'active' : ''}`}
          containerId="main-container"
        >
          How It Works
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;