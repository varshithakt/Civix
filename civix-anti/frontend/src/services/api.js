import axios from 'axios';

const API_BASE = '/api';

export const processNLPQuery = async (queryText) => {
  const res = await axios.post(`${API_BASE}/nlp/process-query`, { query: queryText });
  return res.data;
};

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await axios.post(`${API_BASE}/documents/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const getUploadedDocuments = async () => {
  const res = await axios.get(`${API_BASE}/documents/`);
  return res.data;
};

export const clearUploadedDocuments = async () => {
  const res = await axios.delete(`${API_BASE}/documents/clear`);
  return res.data;
};

export const getAllSchemes = async (category = null) => {
  const url = category ? `${API_BASE}/schemes/?category=${encodeURIComponent(category)}` : `${API_BASE}/schemes/`;
  const res = await axios.get(url);
  return res.data;
};

export const getSchemeDetail = async (schemeId) => {
  const res = await axios.get(`${API_BASE}/schemes/${schemeId}`);
  return res.data;
};

export const matchSchemes = async (profile, query = '') => {
  const res = await axios.post(`${API_BASE}/schemes/match`, { profile, query });
  return res.data;
};

export const getCurrentProfile = async () => {
  const res = await axios.get(`${API_BASE}/profile/`);
  return res.data;
};

export const updateProfile = async (profileData, merge = false) => {
  const res = await axios.post(`${API_BASE}/profile/update`, { ...profileData, merge });
  return res.data;
};

export const getAutofillPreview = async (schemeId, profile) => {
  const res = await axios.post(`${API_BASE}/profile/autofill-preview`, { scheme_id: schemeId, profile });
  return res.data;
};

export const askChatbot = async (message, userProfile = null, selectedSchemeId = null) => {
  const res = await axios.post(`${API_BASE}/chat/ask`, {
    message,
    user_profile: userProfile,
    selected_scheme_id: selectedSchemeId
  });
  return res.data;
};

export const listApplications = async () => {
  const res = await axios.get(`${API_BASE}/applications/`);
  return res.data;
};

export const getApplicationDetail = async (appId) => {
  const res = await axios.get(`${API_BASE}/applications/${appId}`);
  return res.data;
};

export const submitDirectApplication = async (payload) => {
  const res = await axios.post(`${API_BASE}/applications/apply`, payload);
  return res.data;
};

export const advanceApplicationProgress = async (appId) => {
  const res = await axios.post(`${API_BASE}/applications/${appId}/advance`);
  return res.data;
};

export const deleteApplication = async (appId) => {
  const res = await axios.delete(`${API_BASE}/applications/${appId}`);
  return res.data;
};
