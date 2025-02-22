
import './App.css';
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import About from "./components/About";
import Mission from "./components/Mission";
import Footer from "./components/Footer";

function App() {
  return (
    <div className="home-page">
      <Navbar />
      <Hero />
      <About />
      <Mission />
      <Footer />
    </div>
  );
}

export default App;
