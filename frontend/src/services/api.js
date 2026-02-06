import axios from 'axios';

// HARDCODE the URL directly so Vercel has no choice but to use it
const API_BASE_URL = "https://financial-health-ai-bb7t.onrender.com";

export const uploadAndAnalyze = async (file, businessType = "Retail", language = "en") => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('business_type', businessType);
  formData.append('language', language);

  try {
    // We are calling the live Render URL now
    const response = await axios.post(`${API_BASE_URL}/analysis/run`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};