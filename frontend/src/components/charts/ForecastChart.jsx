import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const ForecastChart = ({ data }) => {
  return (
    <div className="bg-[#1e293b] p-6 rounded-2xl border border-slate-700 shadow-xl">
      <h3 className="text-lg font-bold text-white mb-4">3-Month Financial Projection</h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorNet" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" />
            <XAxis 
              dataKey="month" 
              axisLine={false} 
              tickLine={false} 
              tick={{fill: '#94a3b8', fontSize: 12}} 
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{fill: '#94a3b8', fontSize: 12}} 
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1e293b', 
                borderRadius: '12px', 
                border: '1px solid #475569', 
                boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.5)',
                color: '#fff' 
              }}
              itemStyle={{ color: '#fff' }}
            />
            <Legend verticalAlign="top" align="right" height={36} iconType="circle" />
            <Area 
              type="monotone" 
              dataKey="projected_revenue" 
              name="Revenue"
              stroke="#10b981" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorRev)" 
            />
            <Area 
              type="monotone" 
              dataKey="projected_net_cashflow" 
              name="Net Profit"
              stroke="#3b82f6" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorNet)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ForecastChart;