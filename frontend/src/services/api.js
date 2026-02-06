import axios from 'axios';

// Standard Node environment variable (No Vite prefix)
const API_BASE_URL = process.env.REACT_APP_API_URL || "";

export const uploadAndAnalyze = async (file, businessType = "Retail", language = "en") => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('business_type', businessType);
  formData.append('language', language);

  try {
    const response = await axios.post(`${API_BASE_URL}/analysis/run`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};