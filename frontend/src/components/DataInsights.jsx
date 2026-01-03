import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import './DataInsights.css'

function DataInsights() {
    const [activeTab, setActiveTab] = useState('shopping-centers')
    const [filters, setFilters] = useState({ state: '', city: '' })
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState({})

    useEffect(() => {
        loadData()
    }, [activeTab, filters])

    const loadData = async () => {
        setLoading(true)
        try {
            switch (activeTab) {
                case 'shopping-centers':
                    const centers = await api.getShoppingCenters(filters)
                    setData({ shoppingCenters: centers.data })
                    break
                case 'traffic':
                    const traffic = await api.getTrafficData(filters)
                    setData({ trafficData: traffic.data })
                    break
                case 'news':
                    const news = await api.getNewsArticles(filters)
                    setData({ newsArticles: news.data })
                    break
                case 'economics':
                    const economics = await api.getEconomicIndicators(filters)
                    setData({ economicIndicators: economics.data })
                    break
                case 'developments':
                    const projects = await api.getDevelopmentProjects(filters)
                    setData({ developmentProjects: projects.data })
                    break
            }
        } catch (error) {
            console.error('Error loading data:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="data-insights">
            <div className="insights-header">
                <h2>Data Insights</h2>
                <div className="filters">
                    <input
                        type="text"
                        placeholder="State (e.g., FL)"
                        value={filters.state}
                        onChange={(e) => setFilters({ ...filters, state: e.target.value })}
                        className="filter-input"
                    />
                    <input
                        type="text"
                        placeholder="City"
                        value={filters.city}
                        onChange={(e) => setFilters({ ...filters, city: e.target.value })}
                        className="filter-input"
                    />
                    <button onClick={loadData} className="filter-btn">
                        Apply Filters
                    </button>
                </div>
            </div>

            <div className="insights-tabs">
                <button
                    className={activeTab === 'shopping-centers' ? 'active' : ''}
                    onClick={() => setActiveTab('shopping-centers')}
                >
                    Shopping Centers
                </button>
                <button
                    className={activeTab === 'traffic' ? 'active' : ''}
                    onClick={() => setActiveTab('traffic')}
                >
                    Traffic Data
                </button>
                <button
                    className={activeTab === 'news' ? 'active' : ''}
                    onClick={() => setActiveTab('news')}
                >
                    News Articles
                </button>
                <button
                    className={activeTab === 'economics' ? 'active' : ''}
                    onClick={() => setActiveTab('economics')}
                >
                    Economic Indicators
                </button>
                <button
                    className={activeTab === 'developments' ? 'active' : ''}
                    onClick={() => setActiveTab('developments')}
                >
                    Development Projects
                </button>
            </div>

            <div className="insights-content">
                {loading && <div className="loading">Loading data...</div>}

                {activeTab === 'shopping-centers' && data.shoppingCenters && (
                    <div className="data-section">
                        <h3>Shopping Centers ({data.shoppingCenters.length})</h3>
                        <div className="data-grid">
                            {data.shoppingCenters.map((center) => (
                                <div key={center.id} className="data-card">
                                    <h4>{center.name}</h4>
                                    <p className="location">
                                        {center.city}, {center.state}
                                    </p>
                                    {center.co_tenancy_score !== null && (
                                        <div className="score">
                                            <span className="score-label">Co-tenancy Score:</span>
                                            <span className="score-value">{center.co_tenancy_score.toFixed(1)}</span>
                                        </div>
                                    )}
                                    {center.anchor_tenants && center.anchor_tenants.length > 0 && (
                                        <div className="anchors">
                                            <strong>Anchor Tenants:</strong>
                                            <div className="anchor-tags">
                                                {center.anchor_tenants.map((anchor, idx) => (
                                                    <span key={idx} className="anchor-tag">
                                                        {anchor}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {center.rating && (
                                        <div className="rating">
                                            ⭐ {center.rating.toFixed(1)} ({center.user_rating_count || 0} reviews)
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'traffic' && data.trafficData && (
                    <div className="data-section">
                        <h3>Traffic Data ({data.trafficData.length})</h3>
                        <div className="data-table-container">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Location</th>
                                        <th>City</th>
                                        <th>State</th>
                                        <th>Accessibility Score</th>
                                        <th>Avg Daily Traffic</th>
                                        <th>Peak Hour Volume</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.trafficData.map((traffic) => (
                                        <tr key={traffic.id}>
                                            <td>{traffic.location_id || 'N/A'}</td>
                                            <td>{traffic.city}</td>
                                            <td>{traffic.state}</td>
                                            <td>
                                                <div className="score-bar">
                                                    <div
                                                        className="score-fill"
                                                        style={{
                                                            width: `${(traffic.accessibility_score || 0) * 100}%`,
                                                        }}
                                                    ></div>
                                                    <span>{(traffic.accessibility_score || 0).toFixed(2)}</span>
                                                </div>
                                            </td>
                                            <td>{traffic.average_daily_traffic?.toLocaleString() || 'N/A'}</td>
                                            <td>{traffic.peak_hour_volume?.toLocaleString() || 'N/A'}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'news' && data.newsArticles && (
                    <div className="data-section">
                        <h3>News Articles ({data.newsArticles.length})</h3>
                        <div className="news-list">
                            {data.newsArticles.map((article) => (
                                <div key={article.id} className="news-card">
                                    <div className="news-header">
                                        <h4>
                                            <a href={article.url} target="_blank" rel="noopener noreferrer">
                                                {article.title}
                                            </a>
                                        </h4>
                                        <div className="news-meta">
                                            <span className={`sentiment-badge ${article.sentiment}`}>
                                                {article.sentiment}
                                            </span>
                                            <span className={`topic-badge ${article.topic}`}>
                                                {article.topic}
                                            </span>
                                        </div>
                                    </div>
                                    <p className="news-source">
                                        {article.source} • {article.published_date ? new Date(article.published_date).toLocaleDateString() : 'Date unknown'}
                                    </p>
                                    {article.city && article.state && (
                                        <p className="news-location">
                                            📍 {article.city}, {article.state}
                                        </p>
                                    )}
                                    {article.content && (
                                        <p className="news-content">{article.content.substring(0, 200)}...</p>
                                    )}
                                    {article.mentions_publix && (
                                        <span className="publix-mention">🏪 Mentions Publix</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'economics' && data.economicIndicators && (
                    <div className="data-section">
                        <h3>Economic Indicators ({data.economicIndicators.length})</h3>
                        <div className="data-grid">
                            {data.economicIndicators.map((indicator) => (
                                <div key={indicator.id} className="data-card">
                                    <h4>
                                        {indicator.city}, {indicator.state}
                                    </h4>
                                    {indicator.county && <p className="county">County: {indicator.county}</p>}
                                    <div className="indicator-grid">
                                        {indicator.unemployment_rate !== null && (
                                            <div className="indicator-item">
                                                <span className="indicator-label">Unemployment:</span>
                                                <span className="indicator-value">
                                                    {(indicator.unemployment_rate * 100).toFixed(1)}%
                                                </span>
                                            </div>
                                        )}
                                        {indicator.employment_growth_rate !== null && (
                                            <div className="indicator-item">
                                                <span className="indicator-label">Employment Growth:</span>
                                                <span className="indicator-value">
                                                    {(indicator.employment_growth_rate * 100).toFixed(2)}%
                                                </span>
                                            </div>
                                        )}
                                        {indicator.average_wage !== null && (
                                            <div className="indicator-item">
                                                <span className="indicator-label">Avg Wage:</span>
                                                <span className="indicator-value">
                                                    ${indicator.average_wage?.toLocaleString() || 'N/A'}
                                                </span>
                                            </div>
                                        )}
                                        {indicator.retail_sales_per_capita !== null && (
                                            <div className="indicator-item">
                                                <span className="indicator-label">Retail Sales/Capita:</span>
                                                <span className="indicator-value">
                                                    ${indicator.retail_sales_per_capita?.toLocaleString() || 'N/A'}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'developments' && data.developmentProjects && (
                    <div className="data-section">
                        <h3>Development Projects ({data.developmentProjects.length})</h3>
                        <div className="data-grid">
                            {data.developmentProjects.map((project) => (
                                <div key={project.id} className="data-card">
                                    <h4>{project.project_name || 'Unnamed Project'}</h4>
                                    <p className="location">
                                        {project.city}, {project.state}
                                    </p>
                                    {project.address && <p className="address">{project.address}</p>}
                                    <div className="project-details">
                                        {project.project_type && (
                                            <span className={`project-type ${project.project_type}`}>
                                                {project.project_type}
                                            </span>
                                        )}
                                        {project.status && (
                                            <span className={`project-status ${project.status}`}>
                                                {project.status}
                                            </span>
                                        )}
                                    </div>
                                    {project.square_feet && (
                                        <p className="project-size">
                                            Size: {project.square_feet.toLocaleString()} sq ft
                                        </p>
                                    )}
                                    {project.estimated_cost && (
                                        <p className="project-cost">
                                            Est. Cost: ${project.estimated_cost.toLocaleString()}
                                        </p>
                                    )}
                                    {project.developer_name && (
                                        <p className="developer">Developer: {project.developer_name}</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default DataInsights

