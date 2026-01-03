import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts'
import './Dashboard.css'

const COLORS = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']

function EnhancedDashboard() {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        loadDashboardData()
    }, [])

    const loadDashboardData = async () => {
        try {
            setLoading(true)
            const response = await api.getDashboardStats()
            setStats(response.data)
            setError(null)
        } catch (err) {
            setError('Failed to load dashboard data')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return <div className="loading">Loading dashboard...</div>
    }

    if (error) {
        return <div className="error">{error}</div>
    }

    if (!stats) {
        return <div className="loading">No data available</div>
    }

    // Prepare chart data
    const storesByStateData = Object.entries(stats.stores_by_state || {})
        .map(([state, count]) => ({ name: state, value: count }))
        .sort((a, b) => b.value - a.value)

    const competitorsByTypeData = Object.entries(stats.competitors_by_type || {})
        .map(([name, count]) => ({ name, value: count }))
        .sort((a, b) => b.value - a.value)

    const demographicsByStateData = Object.entries(stats.demographics_by_state || {})
        .map(([state, count]) => ({ name: state, value: count }))
        .sort((a, b) => b.value - a.value)

    const parcelsByStateData = Object.entries(stats.parcels_by_state || {})
        .map(([state, count]) => ({ name: state, value: count }))
        .sort((a, b) => b.value - a.value)

    const confidenceData = (stats.recent_predictions || [])
        .slice(0, 10)
        .map((pred) => ({
            name: `${pred.city}, ${pred.state}`,
            confidence: (pred.confidence_score * 100).toFixed(1),
        }))

    return (
        <div className="dashboard">
            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Publix Stores</h3>
                    <p className="stat-value">{stats.total_stores?.toLocaleString() || 0}</p>
                    <p className="stat-label">Across {Object.keys(stats.stores_by_state || {}).length} states</p>
                </div>
                <div className="stat-card">
                    <h3>Competitor Stores</h3>
                    <p className="stat-value">{stats.total_competitors?.toLocaleString() || 0}</p>
                    <p className="stat-label">{Object.keys(stats.competitors_by_type || {}).length} competitor types</p>
                </div>
                <div className="stat-card">
                    <h3>Demographics</h3>
                    <p className="stat-value">{stats.total_demographics?.toLocaleString() || 0}</p>
                    <p className="stat-label">Cities analyzed</p>
                </div>
                <div className="stat-card">
                    <h3>Parcels</h3>
                    <p className="stat-value">{stats.total_parcels?.toLocaleString() || 0}</p>
                    <p className="stat-label">15-25 acre parcels</p>
                </div>
                <div className="stat-card">
                    <h3>Zoning Records</h3>
                    <p className="stat-value">{stats.total_zoning_records?.toLocaleString() || 0}</p>
                    <p className="stat-label">Records collected</p>
                </div>
                <div className="stat-card">
                    <h3>Predictions</h3>
                    <p className="stat-value">{stats.total_predictions?.toLocaleString() || 0}</p>
                    <p className="stat-label">Avg confidence: {(stats.average_confidence * 100).toFixed(1)}%</p>
                </div>
            </div>

            <div className="charts-grid">
                <div className="card">
                    <h2>Publix Stores by State</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={storesByStateData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="value" fill="#3498db" name="Stores" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="card">
                    <h2>Competitor Stores by Type</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={competitorsByTypeData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {competitorsByTypeData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="charts-grid">
                <div className="card">
                    <h2>Demographics Coverage by State</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={demographicsByStateData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="value" fill="#2ecc71" name="Cities" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {parcelsByStateData.length > 0 && (
                    <div className="card">
                        <h2>Parcels by State</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={parcelsByStateData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="value" fill="#9b59b6" name="Parcels" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>

            <div className="charts-grid">
                {confidenceData.length > 0 && (
                    <div className="card">
                        <h2>Top Predictions by Confidence</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={confidenceData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="confidence" fill="#e74c3c" name="Confidence %" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>

            {stats.recent_predictions && stats.recent_predictions.length > 0 && (
                <div className="card">
                    <h2>Recent Predictions</h2>
                    <div className="predictions-list">
                        {stats.recent_predictions.slice(0, 5).map((pred) => (
                            <div key={pred.id} className="prediction-item">
                                <div className="prediction-header">
                                    <h4>{pred.city}, {pred.state}</h4>
                                    <span className="confidence-badge">
                                        {(pred.confidence_score * 100).toFixed(1)}%
                                    </span>
                                </div>
                                <p className="prediction-reasoning">{pred.reasoning}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

export default EnhancedDashboard

