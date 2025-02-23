import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const EcoBarChart = ({ data, title, xLabel, yLabel, colors }) => {
  return (
    <div className="chart-container">
      <h3>{title}</h3>
      <BarChart width={600} height={400} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" label={{ value: xLabel, position: 'bottom' }} />
        <YAxis label={{ value: yLabel, angle: -90, position: 'left' }} />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" fill={colors[0]} />
      </BarChart>
    </div>
  );
};

export default EcoBarChart;