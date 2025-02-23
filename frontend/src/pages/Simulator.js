import React, {useState, useEffect} from "react";
import "./Simulator.css";
import LoadingFlower from "../components/LoadingFlower/LoadingFlower";
import BarChart from "../components/DataReps/BarChart";
import PieChart from "../components/DataReps/PieChart";

const Simulator = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const targetProgress = 75;
  const sampleData = [
    { name: 'Category 1', value: 300 },
    { name: 'Category 2', value: 400 },
    { name: 'Category 3', value: 300 },
    { name: 'Category 4', value: 200 },
  ];

  const colors = ['#0088FE', '#00C49F', '#FFBB28'];

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
        {/* Main simulation content will go here */}
        <div className="simulation-tabs">
          <div className="tab-buttons">
            <button className="tab-button">Tab 1</button>
            <button className="tab-button">Tab 2</button>
            <button className="tab-button">Tab 3</button>
          </div>
          <div className="tab-content">
            {isLoading ? (
              <div className="loading-screen">
                <LoadingFlower />
              </div>
            ) : (
              <div className="simulation-content">
                <BarChart 
                  data={sampleData}
                  title="Species Population"
                  xLabel="Species"
                  yLabel="Population"
                  colors={colors}
                />
                <PieChart
                  data={sampleData}
                  title="Species Distribution"
                  colors={colors}
                />
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="simulation-controls">
        <h2>Controls</h2>
        {/* Control panel content will go here */}
      </div>
    </div>
  );
};

export default Simulator;