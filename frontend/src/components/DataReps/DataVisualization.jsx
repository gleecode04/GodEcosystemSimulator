import React, { useState } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell } from 'recharts';
import { getGreenPaletteArray } from './colors';

const DataVisualization = ({ rawData, visualizationType = 'bar' }) => {
  const [dataType, setDataType] = useState('species');
  const greenColors = getGreenPaletteArray();

  // Process incoming data into chart-friendly format
  const processDataForVisualization = (rawData) => {
    if (!rawData) return [];
    
    return Object.entries(rawData).map(([key, value]) => ({
      name: key,
      value: typeof value === 'number' ? value : parseFloat(value)
    }));
  };

  // Select appropriate data based on type
  const getRelevantData = (dataType) => {
    if (!rawData) return [];

    switch(dataType) {
      case 'species':
        return processDataForVisualization(rawData.speciesData);
      case 'environmental':
        return processDataForVisualization(rawData.environmentalFactors);
      case 'timeSeries':
        return Object.entries(rawData.timeSeriesData || {}).map(([year, data]) => ({
          name: year,
          ...data
        }));
      default:
        return [];
    }
  };

  const getBarColor = (entry, index) => {
    return greenColors[index % greenColors.length];
  };

  // Render different chart types
  const renderChart = () => {
    const data = getRelevantData(dataType);
    
    switch(visualizationType) {
      case 'bar':
        return (
          <BarChart width={600} height={400} data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value">
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={getBarColor(entry, index)}
                />
              ))}
            </Bar>
          </BarChart>
        );
      
      case 'line':
        return (
          <LineChart width={600} height={400} data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke={greenColors[0]} />
          </LineChart>
        );
      
      case 'pie':
        return (
          <PieChart width={400} height={400}>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={150}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`}
                  fill={getBarColor(entry, index)}
                />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        );
      
      default:
        return <div>Please select a visualization type</div>;
    }
  };

  return (
    <div className="data-visualization-container">
      <div className="controls">
        <select 
          value={dataType} 
          onChange={(e) => setDataType(e.target.value)}
          className="data-select"
        >
          <option value="species">Species Population</option>
          <option value="environmental">Environmental Factors</option>
          <option value="timeSeries">Time Series Data</option>
        </select>
      </div>
      
      <div className="chart-container">
        {renderChart()}
      </div>
    </div>
  );
};

export default DataVisualization;