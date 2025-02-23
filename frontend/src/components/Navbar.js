import React, { useState, useEffect } from "react";
import "./Navbar.css";
import { useNavigate } from "react-router-dom";
import { Link, Events, scrollSpy } from "react-scroll";

const Navbar = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('hero');

  useEffect(() => {
    scrollSpy.update();
    Events.scrollEvent.register('begin', (to) => {
      setActiveSection(to);
    });
    Events.scrollEvent.register('end', (to) => {
      setActiveSection(to);
    });
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
          duration={1200}
          className={`nav-link ${activeSection === 'hero-section' ? 'active' : ''}`}
          containerId="main-container"
          ignoreCancelEvents={true}
          spyThrottle={500}
        >
          [ Home ]
        </Link>
        <Link
          activeClass="active"
          to="about-section"
          spy={true}
          smooth={true}
          offset={0}
          duration={1200}
          className={`nav-link ${activeSection === 'about-section' ? 'active' : ''}`}
          containerId="main-container"
          ignoreCancelEvents={true}
          spyThrottle={500}
        >
          [ About ]
        </Link>
        <Link
          activeClass="active"
          to="mission-section"
          spy={true}
          smooth={true}
          offset={0}
          duration={1200}
          className={`nav-link ${activeSection === 'mission-section' ? 'active' : ''}`}
          containerId="main-container"
          ignoreCancelEvents={true}
          spyThrottle={500}
        >
          [ Mission ]
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;