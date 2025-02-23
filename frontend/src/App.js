import './App.css';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import About from "./components/About";
import Mission from "./components/Mission";
import Footer from "./components/Footer";
import Simulator from "./pages/Simulator";
import EarthModelContainer from "./Earth/EarthModelContainer";

function App() {
  return (
    <div className="home-page">
      <Router>
        <Routes>
          <Route path="/" element={
            <>
              <Navbar />
              <EarthModelContainer />
              <div className="main-container" id="main-container">
                <section className="section" id="hero"><Hero /></section>
                <section className="section" id="about"><About /></section>
                <section className="section" id="how-it-works"><Mission /></section>
                <section className="section" id="footer"><Footer /></section>
              </div>
            </>
          } />
          <Route path="/simulator" element={<Simulator />} />
        </Routes>
      </Router>      
    </div>
  );
}

export default App;
