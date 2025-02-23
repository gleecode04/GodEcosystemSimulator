import React, {useState, useEffect} from "react";
import "./Simulator.css";
import MessageBox from "./MessageBox";

const Simulator = () => {
  const [progress, setProgress] = useState(0);
  const targetProgress = 75;

  useEffect(() => {
    const animateProgress = () => {
      if (progress < targetProgress) {
        setProgress(prev => Math.min(prev + 1, targetProgress));
      }
    };

    const timer = setInterval(animateProgress, 20);

    return () => clearInterval(timer);
  }, [progress, targetProgress]);

  return (
    <div className="simulation-container">
      <div className="simulation-main">
        <div className="progress-bar">
          <div className="progress-percentage">{progress}%</div>
          <div className="progress-label">Progress Bar</div>
          <div className="progress-bar-fill" style={{width: `${progress}%`}}></div>
        </div>
        <div className="simulation-tabs">
          <div className="tab-buttons">
            <button className="tab-button">Tab 1</button>
            <button className="tab-button">Tab 2</button>
            <button className="tab-button">Tab 3</button>
          </div>
          <div className="tab-content">

          </div>
        </div>
      </div>
      <div className="simulation-controls">
        <MessageBox />
      </div>
    </div>
  );
};

export default Simulator;