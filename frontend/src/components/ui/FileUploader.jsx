import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, Loader2 } from 'lucide-react';

const FileUploader = ({ onUploadSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      // Logic to call api.js will go here
      const data = await onUploadSuccess(file);
    } catch (err) {
      alert("Upload failed. Check console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-8 border-2 border-dashed border-slate-300 rounded-2xl bg-white text-center">
      <Upload className="mx-auto h-12 w-12 text-slate-400 mb-4" />
      <h2 className="text-xl font-semibold text-slate-700">Upload Financial Data</h2>
      <p className="text-sm text-slate-500 mb-6">Support CSV, XLSX, or PDF exports</p>
      
      <input 
        type="file" 
        onChange={handleFileChange} 
        className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 mb-4"
      />

      {file && !loading && (
        <button 
          onClick={handleUpload}
          className="w-full bg-slate-900 text-white py-3 rounded-xl font-medium hover:bg-slate-800 transition"
        >
          Analyze {file.name}
        </button>
      )}

      {loading && (
        <div className="flex items-center justify-center gap-2 text-blue-600 font-medium">
          <Loader2 className="animate-spin" /> processing with AI...
        </div>
      )}
    </div>
  );
};

export default FileUploader;