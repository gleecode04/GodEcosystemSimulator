import React, {useState, useEffect} from "react";
import "./Simulator.css";
import MessageBox from "./MessageBox";
import LoadingFlower from "../components/LoadingFlower/LoadingFlower";
import DataVisualization from '../components/DataReps/DataVisualization';
import { useNavigate } from 'react-router-dom';

const Simulator = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const targetProgress = 75;
  const [activeTab, setActiveTab] = useState(1);

  const mockData = {
    speciesData: {
      "Arctic Fox": 1200,
      "Polar Bear": 300,
      "Seal": 5000,
    },
    environmentalFactors: {
      "Temperature": -5,
      "Ice Coverage": 75,
      "Food Availability": 60,
    },
    timeSeriesData: {
      "2020": { population: 1000, biodiversity: 0.8 },
      "2021": { population: 950, biodiversity: 0.75 },
    }
  };

  useEffect(() => {
    const animateProgress = () => {
      if (progress < targetProgress) {
        setProgress(prev => Math.min(prev + 1, targetProgress));
      }
    };

    const timer = setInterval(animateProgress, 20);

    return () => clearInterval(timer);
  }, [progress, targetProgress]);

  const renderTabContent = () => {
    switch(activeTab) {
      case 1:
        return (
          <div className="tab-content">
            <h2>Species Data</h2>
            <DataVisualization 
              rawData={mockData} 
              visualizationType="bar"
            />
          </div>
        );
      case 2:
        return (
          <div className="tab-content">
            <h2>Environmental Factors</h2>
            <DataVisualization 
              rawData={mockData} 
              visualizationType="pie"
            />
          </div>
        );
      case 3:
        return (
          <div className="tab-content">
            <h2>Time Series Analysis</h2>
            <DataVisualization 
              rawData={mockData} 
              visualizationType="line"
            />
          </div>
        );
      default:
        return <div>Select a tab</div>;
    }
  };

  return (
    <div className="simulation-container">
      <div className="simulation-main">
        <div className="simulation-header">
          <button 
            className="ecosim-button"
            onClick={() => navigate('/')}
          >
            ECOSIM
          </button>
          
          <div className="progress-bar-container">
            <div className="progress-bar">
              <div className="progress-percentage">{progress}%</div>
              <div className="progress-label">Progress Bar</div>
              <div className="progress-bar-fill" style={{width: `${progress}%`}}></div>
            </div>
          </div>
        </div>

        <div className="tab-buttons">
          <button 
            className={`tab-button ${activeTab === 1 ? 'active' : ''}`}
            onClick={() => setActiveTab(1)}
          >
            Species Data
          </button>
          <button 
            className={`tab-button ${activeTab === 2 ? 'active' : ''}`}
            onClick={() => setActiveTab(2)}
          >
            Environmental Data
          </button>
          <button 
            className={`tab-button ${activeTab === 3 ? 'active' : ''}`}
            onClick={() => setActiveTab(3)}
          >
            Time Series
          </button>
        </div>
        
        <div className="tab-content-container">
          {renderTabContent()}
        </div>
      </div>
      <div className="simulation-controls">
        <MessageBox />
      </div>
    </div>
  );
};

export default Simulator;