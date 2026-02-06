import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const CreditScoreGauge = ({ score, grade }) => {
  const data = [
    { value: score },
    { value: 100 - score },
  ];

  // Using darker Slate for the empty part of the gauge
  const COLORS = grade === 'A' ? ['#10b981', '#334155'] : 
                 grade === 'B' ? ['#3b82f6', '#334155'] : 
                 grade === 'C' ? ['#f59e0b', '#334155'] : ['#ef4444', '#334155'];

  return (
    <div className="bg-[#1e293b] p-6 rounded-2xl border border-slate-700 shadow-xl text-center">
      <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-2">Credit Readiness</h3>
      <div className="h-40 w-full relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="100%"
              startAngle={180}
              endAngle={0}
              innerRadius={60}
              outerRadius={80}
              paddingAngle={0}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="none" />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-2">
          <span className="text-4xl font-black text-white">{grade}</span>
          <span className="text-xs text-slate-400 font-medium tracking-tight">Score: {score}/100</span>
        </div>
      </div>
      <p className="mt-4 text-xs text-slate-400 leading-relaxed px-2">
        Grade based on debt-ratio, stability, and risk profile.
      </p>
    </div>
  );
};

export default CreditScoreGauge;