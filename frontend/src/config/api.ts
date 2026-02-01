/**
 * API Configuration
 * 
 * Uses environment variable in production (Render deployment)
 * Falls back to localhost for local development
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const API_URL = `${API_BASE_URL}/api`;
