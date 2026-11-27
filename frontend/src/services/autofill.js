import axios from "axios";

const API_BASE = "/api";

export const getAutofillPreview = async (schemeId, editedProfile = {}) => {
  const response = await axios.post(`${API_BASE}/autofill/preview`, {
    scheme_id: schemeId,
    edited_profile: editedProfile
  });
  return response.data;
};

export const getAutofillProfile = async () => {
  const response = await axios.get(`${API_BASE}/profile/`);
  return response.data.profile || {};
};

export const getAutofillSchemes = async () => {
  const response = await axios.get(`${API_BASE}/schemes/`);
  return response.data.schemes || [];
};
