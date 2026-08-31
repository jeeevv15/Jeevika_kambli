import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || "http://localhost:8000",
});

export const getOverview = () => api.get("/api/overview").then((r) => r.data);
export const getTaxonomy = () => api.get("/api/taxonomy").then((r) => r.data);
export const getSimulateOptions = () => api.get("/api/simulate/options").then((r) => r.data);
export const postSimulate = (body) => api.post("/api/simulate", body).then((r) => r.data);
export const getLiveFeed = (n = 40) => api.get(`/api/live-feed?n=${n}`).then((r) => r.data);
export const getTransaction = (id) => api.get(`/api/transaction/${id}`).then((r) => r.data);
export const getAnalytics = () => api.get("/api/analytics").then((r) => r.data);
export const getClosedLoop = () => api.get("/api/closed-loop").then((r) => r.data);
export const getAlerts = () => api.get("/api/alerts").then((r) => r.data);
export const postRunLoop = (body) => api.post("/api/run-loop", body).then((r) => r.data);
export const getObservabilityLogs = () => api.get("/api/observability/logs").then((r) => r.data);
export const getSystemHealth = () => api.get("/api/system-health").then((r) => r.data);
export const getModelInsights = () => api.get("/api/model-insights").then((r) => r.data);

export default api;