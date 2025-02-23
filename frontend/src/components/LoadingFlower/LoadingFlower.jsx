import React from 'react';
import './LoadingFlower.css';

const LoadingFlower = () => {
  return (
    <div className="loading-container">
      <div className="flower">
        <div className="petal petal1"></div>
        <div className="petal petal2"></div>
        <div className="petal petal3"></div>
        <div className="petal petal4"></div>
        <div className="petal petal5"></div>
        <div className="petal petal6"></div>
        <div className="petal petal7"></div>
        <div className="petal petal8"></div>
        <div className="center"></div>
      </div>
      <div className="loading-text">Loading...</div>
    </div>
  );
};

export default LoadingFlower;