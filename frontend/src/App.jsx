import React, { useState } from 'react';
import FileUploader from './components/ui/FileUploader';
import CreditScoreGauge from './components/summary/CreditScoreGauge';
import MetricsGrid from './components/summary/MetricsGrid';
import ForecastChart from './components/charts/ForecastChart';
import { uploadAndAnalyze } from './services/api';
import { Languages, Moon, Sun } from 'lucide-react';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState('en');

  const handleAnalysis = async (file) => {
    setLoading(true);
    try {
      const data = await uploadAndAnalyze(file, "Retail", lang);
      setResult(data);
    } catch (err) {
      alert("Error connecting to backend. See console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans">
      {/* Header */}
      <header className="bg-[#1e293b]/50 border-b border-slate-700 py-4 px-8 sticky top-0 z-10 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-1.5 rounded-lg"><Moon size={20} className="text-white"/></div>
            <h1 className="text-xl font-bold tracking-tight text-white">SME<span className="text-blue-500">Pulse</span> AI</h1>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Language Toggle */}
            <div className="flex items-center bg-slate-800 rounded-lg p-1 border border-slate-700">
              <button 
                onClick={() => setLang('en')}
                className={`px-3 py-1 text-xs rounded-md transition ${lang === 'en' ? 'bg-blue-600 text-white' : 'text-slate-400'}`}
              >
                EN
              </button>
              <button 
                onClick={() => setLang('hi')}
                className={`px-3 py-1 text-xs rounded-md transition ${lang === 'hi' ? 'bg-blue-600 text-white' : 'text-slate-400'}`}
              >
                हिन्दी
              </button>
            </div>
            {result && <button onClick={() => setResult(null)} className="text-sm font-semibold text-blue-400 hover:text-blue-300">New Scan</button>}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 md:p-8">
        {!result ? (
          <div className="flex flex-col items-center justify-center py-24">
            <h2 className="text-5xl font-black text-center mb-6 text-white leading-tight">
              Master Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Financial Future.</span>
            </h2>
            <p className="text-slate-400 text-center mb-10 max-w-lg text-lg">
              {lang === 'hi' ? 'एआई-संचालित स्वास्थ्य मूल्यांकन प्राप्त करने के लिए अपना विवरण अपलोड करें।' : 'Upload bank statements for AI-powered health assessment and credit scoring.'}
            </p>
            <div className="bg-[#1e293b] p-8 rounded-3xl border border-slate-700 shadow-2xl w-full max-w-xl">
              <FileUploader onUploadSuccess={handleAnalysis} />
            </div>
          </div>
        ) : (
          <div className="space-y-6 animate-in fade-in zoom-in-95 duration-500">
            {/* Stats Row */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <div className="lg:col-span-1 bg-[#1e293b] rounded-2xl border border-slate-700 overflow-hidden">
                <CreditScoreGauge score={result.credit_readiness.score} grade={result.credit_readiness.grade} isDark={true} />
              </div>
              <div className="lg:col-span-3">
                <MetricsGrid metrics={result.financial_summary.metrics} isDark={true} />
              </div>
            </div>

            {/* AI & Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-[#1e293b] p-2 rounded-2xl border border-slate-700">
                <ForecastChart data={result.projections} isDark={true} />
              </div>
              <div className="bg-gradient-to-br from-blue-700 to-indigo-900 p-8 rounded-2xl shadow-xl flex flex-col justify-between border border-blue-500/30">
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <Languages size={20} className="text-blue-200" />
                    <h3 className="text-xl font-bold text-white">{lang === 'hi' ? 'एआई अंतर्दृष्टि' : 'AI Insights'}</h3>
                  </div>
                  <p className="text-blue-50 text-md leading-relaxed font-medium italic">
                    "{result.ai_report}"
                  </p>
                </div>
                <div className="mt-6 flex justify-between items-center text-[10px] text-blue-300 uppercase tracking-widest font-bold">
                  <span>Deterministic Logic</span>
                  <span>Gemini 2.5 Verified</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;