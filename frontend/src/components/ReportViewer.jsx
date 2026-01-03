import React, { useState } from 'react'
import { api } from '../services/api'
import './ReportViewer.css'

function ReportViewer() {
    const [region, setRegion] = useState('')
    const [analysisResult, setAnalysisResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleAnalyze = async () => {
        if (!region.trim()) {
            setError('Please enter a region (state)')
            return
        }

        try {
            setLoading(true)
            setError(null)
            const response = await api.triggerAnalysis({ region })
            setAnalysisResult(response.data)
        } catch (err) {
            setError('Failed to run analysis')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="report-viewer">
            <div className="card">
                <h2>Generate Expansion Analysis Report</h2>
                <div className="analysis-controls">
                    <input
                        type="text"
                        placeholder="Enter state (e.g., KY, FL, GA)"
                        value={region}
                        onChange={(e) => setRegion(e.target.value)}
                        className="region-input"
                    />
                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="analyze-btn"
                    >
                        {loading ? 'Analyzing...' : 'Run Analysis'}
                    </button>
                </div>

                {error && <div className="error">{error}</div>}
            </div>

            {analysisResult && (
                <div className="card">
                    <h2>Analysis Results</h2>
                    <div className="analysis-info">
                        <p><strong>Region:</strong> {analysisResult.analysis_data?.region || region}</p>
                        <p><strong>Status:</strong> {analysisResult.status}</p>
                        <p><strong>Predictions Generated:</strong> {analysisResult.predictions?.length || 0}</p>
                    </div>

                    {analysisResult.report && (
                        <div className="report-content">
                            <h3>Report</h3>
                            <div className="report-text">
                                {typeof analysisResult.report === 'string'
                                    ? analysisResult.report
                                    : JSON.stringify(analysisResult.report, null, 2)}
                            </div>
                        </div>
                    )}

                    {analysisResult.predictions && analysisResult.predictions.length > 0 && (
                        <div className="predictions-section">
                            <h3>Top Predictions</h3>
                            <div className="predictions-list">
                                {analysisResult.predictions.slice(0, 10).map((pred) => (
                                    <div key={pred.id} className="prediction-card">
                                        <div className="prediction-header">
                                            <h4>{pred.city}, {pred.state}</h4>
                                            <span className="confidence-badge">
                                                {(pred.confidence_score * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <p className="prediction-reasoning">{pred.reasoning}</p>
                                        {pred.key_factors && (
                                            <div className="key-factors">
                                                <strong>Key Factors:</strong>
                                                <ul>
                                                    {Array.isArray(pred.key_factors)
                                                        ? pred.key_factors.map((factor, i) => (
                                                            <li key={i}>{factor}</li>
                                                        ))
                                                        : Object.entries(pred.key_factors).map(([key, value]) => (
                                                            <li key={key}>
                                                                <strong>{key}:</strong> {value}
                                                            </li>
                                                        ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

export default ReportViewer

