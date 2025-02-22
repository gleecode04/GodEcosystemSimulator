import './App.css';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import About from "./components/About";
import Mission from "./components/Mission";
import Footer from "./components/Footer";
import Simulator from "./pages/Simulator";

function App() {
  return (
    <div className="home-page">
      <Router>
        <Routes>
          <Route path="/" element={
            <>
              <Navbar />
              <Hero />
              <About />
              <Mission />
              <Footer />
            </>
          } />
          <Route path="/simulator" element={<Simulator />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
