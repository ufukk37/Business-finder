import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // İleride auth token eklenebilir
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Bir hata oluştu';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

// ============ Search API ============

export const searchBusinesses = async (params) => {
  const response = await api.post('/search/', params);
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get('/search/categories');
  return response.data;
};

export const getSearchHistory = async (limit = 20) => {
  const response = await api.get(`/search/history?limit=${limit}`);
  return response.data;
};

export const getRateLimitStatus = async () => {
  const response = await api.get('/search/rate-limit-status');
  return response.data;
};

// ============ Business API ============

export const getBusinesses = async (params = {}) => {
  const queryParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      queryParams.append(key, value);
    }
  });
  
  const response = await api.get(`/businesses/?${queryParams}`);
  return response.data;
};

export const getBusiness = async (id) => {
  const response = await api.get(`/businesses/${id}`);
  return response.data;
};

export const updateBusiness = async (id, data) => {
  const response = await api.patch(`/businesses/${id}`, data);
  return response.data;
};

export const deleteBusiness = async (id) => {
  const response = await api.delete(`/businesses/${id}`);
  return response.data;
};

export const getDashboardStats = async () => {
  const response = await api.get('/businesses/stats');
  return response.data;
};

// ============ Tags API ============

export const addTag = async (businessId, tag) => {
  const response = await api.post(`/businesses/${businessId}/tags`, { tag });
  return response.data;
};

export const removeTag = async (businessId, tag) => {
  const response = await api.delete(`/businesses/${businessId}/tags/${tag}`);
  return response.data;
};

// ============ Notes API ============

export const addNote = async (businessId, note) => {
  const response = await api.post(`/businesses/${businessId}/notes`, { note });
  return response.data;
};

export const deleteNote = async (businessId, noteId) => {
  const response = await api.delete(`/businesses/${businessId}/notes/${noteId}`);
  return response.data;
};

// ============ Export API ============

export const exportBusinesses = async (format) => {
  const response = await api.get(`/exports/download/${format}`, {
    responseType: 'blob',
  });
  return response;
};

export const getExportFields = async () => {
  const response = await api.get('/exports/fields');
  return response.data;
};

export default api;
