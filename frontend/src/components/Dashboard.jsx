import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import './Dashboard.css'

function Dashboard() {
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
    const confidenceData = stats.recent_predictions
        .slice(0, 10)
        .map((pred, index) => ({
            name: `${pred.city}, ${pred.state}`,
            confidence: (pred.confidence_score * 100).toFixed(1),
        }))

    return (
        <div className="dashboard">
            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Total Stores</h3>
                    <p className="stat-value">{stats.total_stores}</p>
                </div>
                <div className="stat-card">
                    <h3>Total Predictions</h3>
                    <p className="stat-value">{stats.total_predictions}</p>
                </div>
                <div className="stat-card">
                    <h3>Average Confidence</h3>
                    <p className="stat-value">{(stats.average_confidence * 100).toFixed(1)}%</p>
                </div>
            </div>

            <div className="card">
                <h2>Top Predictions by Confidence</h2>
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={confidenceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="confidence" fill="#3498db" name="Confidence %" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

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
        </div>
    )
}

export default Dashboard

