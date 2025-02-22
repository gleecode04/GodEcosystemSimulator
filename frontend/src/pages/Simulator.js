import {useState} from "react";

const Simulator = () => {
  const [co2Level, setCo2Level] = useState(20); // Replace with real data later

  return (
    <div className="flex h-screen bg-gray-200">
      {/* Main Simulation Panel */}
      <div className="w-3/4 bg-white p-4">
        {/* Top Navigation Bar */}
        <div className="flex justify-between items-center bg-gray-300 p-2 rounded">
          <button className="p-2 bg-gray-400 rounded">CO₂</button>
          <button className="p-2 bg-gray-400 rounded">Biodiversity</button>
          <button className="p-2 bg-gray-400 rounded">...</button>
        </div>

        {/* Graph Display (Placeholder for now) */}
        <div className="mt-4 p-4 bg-gray-100 rounded-lg">
          <p className="text-lg font-bold">Graph Placeholder</p>
          {/* Later: Insert Recharts or another graphing library here */}
        </div>

        {/* Progress Bar (Health Bar) */}
        <div className="mt-4 p-2 bg-gray-300 rounded-lg">
          <div className="h-4 bg-green-500" style={{ width: `${co2Level}%` }}></div>
          <p className="text-center text-sm mt-1">{co2Level}%</p>
        </div>
      </div>

      {/* Chatbox Placeholder (Will implement later) */}
      <div className="w-1/4 bg-gray-100 p-4">
        <p className="text-lg font-bold">Chatbox Placeholder</p>
      </div>
    </div>
  );
};

export default Simulator;
