import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Wallet } from 'lucide-react';

const MetricCard = ({ title, value, isPositive, icon: Icon }) => (
  <div className="bg-[#1e293b] p-6 rounded-2xl border border-slate-700 shadow-xl transition-transform hover:scale-[1.02]">
    <div className="flex justify-between items-start mb-4">
      <div className={`p-2 rounded-xl ${isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
        <Icon size={22} />
      </div>
      <div className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${isPositive ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
        {isPositive ? 'HEALTHY' : 'STRESS'}
      </div>
    </div>
    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{title}</p>
    <p className="text-2xl font-black text-white mt-1">₹{Number(value).toLocaleString()}</p>
  </div>
);

const MetricsGrid = ({ metrics }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <MetricCard title="Total Revenue" value={metrics.total_revenue || 0} isPositive={true} icon={TrendingUp} />
      <MetricCard title="Net Cashflow" value={metrics.net_cashflow || 0} isPositive={metrics.net_cashflow > 0} icon={Wallet} />
      <MetricCard title="Total Expenses" value={metrics.total_expenses || 0} isPositive={false} icon={TrendingDown} />
      <MetricCard title="Avg Transaction" value={metrics.avg_transaction || 0} isPositive={true} icon={DollarSign} />
    </div>
  );
};

export default MetricsGrid;