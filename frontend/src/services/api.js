/** API client for backend communication */
import axios from 'axios'

// Get API URL from environment variable (set at build time for App Runner)
// Fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL ||
    import.meta.env.PROD ?
    'https://your-backend-apprunner-url.run.app/api' :
    'http://localhost:8000/api'

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
    }
)

export const api = {
    // Stores
    getStores: (params = {}) => apiClient.get('/stores', { params }),

    // Predictions
    getPredictions: (params = {}) => apiClient.get('/predictions', { params }),

    // Analysis
    triggerAnalysis: (data) => apiClient.post('/analyze', data),
    analyzeCity: (data) => apiClient.post('/analyze/city', data),

    // Demographics
    getDemographics: (city, state) =>
        apiClient.get(`/demographics/${city}`, { params: { state } }),

    // Zoning
    getZoningRecords: (region, params = {}) =>
        apiClient.get(`/zoning/${region}`, { params }),

    // Dashboard
    getDashboardStats: () => apiClient.get('/dashboard/stats'),

    // Competitors
    getCompetitors: (params = {}) => apiClient.get('/competitors', { params }),

    // Demographics
    getDemographicsList: (params = {}) => apiClient.get('/demographics', { params }),

    // Parcels
    getParcels: (params = {}) => apiClient.get('/parcels', { params }),

    // Smarty API
    geocodeAddress: (address, city, state, zipCode) =>
        apiClient.post('/smarty/geocode', null, {
            params: { address, city, state, zip_code: zipCode },
        }),
    getPropertyData: (address, city, state, zipCode) =>
        apiClient.post('/smarty/property', null, {
            params: { address, city, state, zip_code: zipCode },
        }),
    searchParcelsSmarty: (city, state, minAcreage = 15.0, maxAcreage = 25.0) =>
        apiClient.post('/smarty/search-parcels', null, {
            params: { city, state, min_acreage: minAcreage, max_acreage: maxAcreage },
        }),

    // Chat
    chat: (message, conversationHistory = null) =>
        apiClient.post('/chat', {
            message,
            conversation_history: conversationHistory,
        }),
    chatSimple: (message) =>
        apiClient.post('/chat/simple', null, {
            params: { message },
        }),

    // Advanced Analytics
    getHeatmap: (state = null) =>
        apiClient.get('/analytics/heatmap', {
            params: state ? { state } : {},
        }),
    getMarketSaturation: (state = null) =>
        apiClient.get('/analytics/market-saturation', {
            params: state ? { state } : {},
        }),
    getCompetitiveLandscape: (state = null) =>
        apiClient.get('/analytics/competitive-landscape', {
            params: state ? { state } : {},
        }),
    calculateROI: (city, state, options = {}) =>
        apiClient.get('/analytics/roi-calculator', {
            params: {
                city,
                state,
                estimated_store_size: options.estimated_store_size || 45000,
                land_cost_per_acre: options.land_cost_per_acre || 500000,
                construction_cost_per_sqft: options.construction_cost_per_sqft || 200,
            },
        }),
    getTrends: (state = null, years = 5) =>
        apiClient.get('/analytics/trends', {
            params: state ? { state, years } : { years },
        }),

    // New Data Collection Endpoints
    getShoppingCenters: (params = {}) =>
        apiClient.get('/shopping-centers', { params }),
    getTrafficData: (params = {}) =>
        apiClient.get('/traffic-data', { params }),
    getNewsArticles: (params = {}) =>
        apiClient.get('/news', { params }),
    getEconomicIndicators: (params = {}) =>
        apiClient.get('/economic-indicators', { params }),
    getDevelopmentProjects: (params = {}) =>
        apiClient.get('/development-projects', { params }),
}

export default apiClient

