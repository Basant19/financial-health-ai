import axios from 'axios';

const API_BASE_URL = "http://localhost:8000";

// Ensure the name matches what you import in App.jsx
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