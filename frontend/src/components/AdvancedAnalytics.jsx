import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts'
import './AdvancedAnalytics.css'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']

function AdvancedAnalytics() {
    const [activeTab, setActiveTab] = useState('heatmap')
    const [heatmapData, setHeatmapData] = useState(null)
    const [saturationData, setSaturationData] = useState(null)
    const [competitiveData, setCompetitiveData] = useState(null)
    const [trendsData, setTrendsData] = useState(null)
    const [roiData, setRoiData] = useState(null)
    const [selectedState, setSelectedState] = useState('')
    const [loading, setLoading] = useState(false)
    const [roiInputs, setRoiInputs] = useState({
        city: '',
        state: '',
        estimated_store_size: 45000,
        land_cost_per_acre: 500000,
        construction_cost_per_sqft: 200,
    })

    useEffect(() => {
        loadData()
    }, [selectedState, activeTab])

    const loadData = async () => {
        setLoading(true)
        try {
            switch (activeTab) {
                case 'heatmap':
                    const heatmap = await api.getHeatmap(selectedState || null)
                    setHeatmapData(heatmap.data)
                    break
                case 'saturation':
                    const saturation = await api.getMarketSaturation(selectedState || null)
                    setSaturationData(saturation.data)
                    break
                case 'competitive':
                    const competitive = await api.getCompetitiveLandscape(selectedState || null)
                    setCompetitiveData(competitive.data)
                    break
                case 'trends':
                    const trends = await api.getTrends(selectedState || null)
                    setTrendsData(trends.data)
                    break
            }
        } catch (error) {
            console.error('Error loading analytics:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleRoiCalculate = async () => {
        if (!roiInputs.city || !roiInputs.state) {
            alert('Please enter city and state')
            return
        }
        setLoading(true)
        try {
            const result = await api.calculateROI(
                roiInputs.city,
                roiInputs.state,
                {
                    estimated_store_size: roiInputs.estimated_store_size,
                    land_cost_per_acre: roiInputs.land_cost_per_acre,
                    construction_cost_per_sqft: roiInputs.construction_cost_per_sqft,
                }
            )
            setRoiData(result.data)
        } catch (error) {
            console.error('Error calculating ROI:', error)
            alert('Error calculating ROI. Make sure demographics data exists for this city.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="advanced-analytics">
            <div className="analytics-header">
                <h2>Advanced Analytics Dashboard</h2>
                <div className="state-filter">
                    <label>Filter by State:</label>
                    <select
                        value={selectedState}
                        onChange={(e) => setSelectedState(e.target.value)}
                    >
                        <option value="">All States</option>
                        <option value="FL">Florida</option>
                        <option value="GA">Georgia</option>
                        <option value="AL">Alabama</option>
                        <option value="SC">South Carolina</option>
                        <option value="NC">North Carolina</option>
                        <option value="TN">Tennessee</option>
                        <option value="VA">Virginia</option>
                        <option value="KY">Kentucky</option>
                    </select>
                </div>
            </div>

            <div className="analytics-tabs">
                <button
                    className={activeTab === 'heatmap' ? 'active' : ''}
                    onClick={() => setActiveTab('heatmap')}
                >
                    Expansion Heat Map
                </button>
                <button
                    className={activeTab === 'saturation' ? 'active' : ''}
                    onClick={() => setActiveTab('saturation')}
                >
                    Market Saturation
                </button>
                <button
                    className={activeTab === 'competitive' ? 'active' : ''}
                    onClick={() => setActiveTab('competitive')}
                >
                    Competitive Landscape
                </button>
                <button
                    className={activeTab === 'trends' ? 'active' : ''}
                    onClick={() => setActiveTab('trends')}
                >
                    Trends & Growth
                </button>
                <button
                    className={activeTab === 'roi' ? 'active' : ''}
                    onClick={() => setActiveTab('roi')}
                >
                    ROI Calculator
                </button>
            </div>

            <div className="analytics-content">
                {loading && <div className="loading">Loading analytics data...</div>}

                {activeTab === 'heatmap' && heatmapData && (
                    <div className="heatmap-section">
                        <h3>Expansion Probability Heat Map</h3>
                        <p>
                            Showing {heatmapData.total_points} locations with expansion potential.
                            Intensity indicates confidence/opportunity score.
                        </p>
                        <div className="heatmap-legend">
                            <span className="legend-item">
                                <span className="legend-color prediction"></span>
                                Predictions (High Confidence)
                            </span>
                            <span className="legend-item">
                                <span className="legend-color opportunity"></span>
                                Opportunities (No Stores Yet)
                            </span>
                        </div>
                        <div className="heatmap-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>City</th>
                                        <th>State</th>
                                        <th>Type</th>
                                        <th>Intensity</th>
                                        <th>Confidence</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {heatmapData.heatmap_points
                                        .sort((a, b) => b.intensity - a.intensity)
                                        .slice(0, 50)
                                        .map((point, idx) => (
                                            <tr key={idx}>
                                                <td>{point.city}</td>
                                                <td>{point.state}</td>
                                                <td>
                                                    <span
                                                        className={`type-badge ${point.type}`}
                                                    >
                                                        {point.type}
                                                    </span>
                                                </td>
                                                <td>
                                                    <div className="intensity-bar">
                                                        <div
                                                            className="intensity-fill"
                                                            style={{
                                                                width: `${point.intensity * 100}%`,
                                                            }}
                                                        ></div>
                                                        <span>{point.intensity.toFixed(2)}</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    {point.value
                                                        ? `${(point.value * 100).toFixed(1)}%`
                                                        : 'N/A'}
                                                </td>
                                            </tr>
                                        ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'saturation' && saturationData && (
                    <div className="saturation-section">
                        <h3>Market Saturation Analysis</h3>
                        <p>
                            Cities ranked by saturation (lowest = highest opportunity).
                            Shows stores per 100K population.
                        </p>
                        <div className="saturation-charts">
                            <div className="chart-container">
                                <h4>Top Opportunities (Lowest Saturation)</h4>
                                <ResponsiveContainer width="100%" height={400}>
                                    <BarChart data={saturationData.saturation_analysis.slice(0, 20)}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis
                                            dataKey="city"
                                            angle={-45}
                                            textAnchor="end"
                                            height={100}
                                        />
                                        <YAxis />
                                        <Tooltip />
                                        <Legend />
                                        <Bar dataKey="stores_per_100k" fill="#8884d8" name="Stores per 100K" />
                                        <Bar dataKey="saturation_score" fill="#82ca9d" name="Saturation Score" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                            <div className="chart-container">
                                <h4>Saturation Distribution</h4>
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={saturationData.saturation_analysis}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="saturation_score" />
                                        <YAxis />
                                        <Tooltip />
                                        <Bar dataKey="publix_stores" fill="#0088FE" name="Publix Stores" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                        <div className="saturation-table">
                            <h4>Detailed Saturation Data</h4>
                            <table>
                                <thead>
                                    <tr>
                                        <th>City</th>
                                        <th>State</th>
                                        <th>Publix Stores</th>
                                        <th>Competitors</th>
                                        <th>Population</th>
                                        <th>Stores/100K</th>
                                        <th>Saturation</th>
                                        <th>Opportunity</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {saturationData.saturation_analysis.slice(0, 50).map((city, idx) => (
                                        <tr key={idx}>
                                            <td>{city.city}</td>
                                            <td>{city.state}</td>
                                            <td>{city.publix_stores}</td>
                                            <td>{city.competitor_stores}</td>
                                            <td>{city.population?.toLocaleString()}</td>
                                            <td>{city.stores_per_100k}</td>
                                            <td>
                                                <div className="saturation-bar">
                                                    <div
                                                        className="saturation-fill"
                                                        style={{
                                                            width: `${city.saturation_score * 100}%`,
                                                            backgroundColor:
                                                                city.saturation_score < 0.3
                                                                    ? '#00C49F'
                                                                    : city.saturation_score < 0.6
                                                                        ? '#FFBB28'
                                                                        : '#FF8042',
                                                        }}
                                                    ></div>
                                                    <span>{(city.saturation_score * 100).toFixed(1)}%</span>
                                                </div>
                                            </td>
                                            <td>
                                                <span
                                                    className={`opportunity-badge ${city.opportunity}`}
                                                >
                                                    {city.opportunity}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'competitive' && competitiveData && (
                    <div className="competitive-section">
                        <h3>Competitive Landscape Analysis</h3>
                        <div className="competitive-stats">
                            <div className="stat-card">
                                <h4>Total Stores</h4>
                                <p className="stat-value">{competitiveData.total_stores}</p>
                            </div>
                            <div className="stat-card">
                                <h4>Overlap Cities</h4>
                                <p className="stat-value">{competitiveData.total_overlap_cities}</p>
                            </div>
                        </div>
                        <div className="competitive-charts">
                            <div className="chart-container">
                                <h4>Market Share</h4>
                                <ResponsiveContainer width="100%" height={400}>
                                    <PieChart>
                                        <Pie
                                            data={competitiveData.market_share}
                                            cx="50%"
                                            cy="50%"
                                            labelLine={false}
                                            label={({ competitor, market_share }) =>
                                                `${competitor}: ${market_share}%`
                                            }
                                            outerRadius={120}
                                            fill="#8884d8"
                                            dataKey="market_share"
                                        >
                                            {competitiveData.market_share.map((entry, index) => (
                                                <Cell
                                                    key={`cell-${index}`}
                                                    fill={COLORS[index % COLORS.length]}
                                                />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                            <div className="chart-container">
                                <h4>Store Counts by Competitor</h4>
                                <ResponsiveContainer width="100%" height={400}>
                                    <BarChart data={competitiveData.market_share}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="competitor" />
                                        <YAxis />
                                        <Tooltip />
                                        <Bar dataKey="count" fill="#0088FE" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                        <div className="overlap-table">
                            <h4>Cities with Publix and Competitors</h4>
                            <table>
                                <thead>
                                    <tr>
                                        <th>City</th>
                                        <th>State</th>
                                        <th>Publix Stores</th>
                                        <th>Competitor Stores</th>
                                        <th>Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {competitiveData.overlap_cities.slice(0, 50).map((city, idx) => (
                                        <tr key={idx}>
                                            <td>{city.city}</td>
                                            <td>{city.state}</td>
                                            <td>{city.publix_stores}</td>
                                            <td>{city.competitor_stores}</td>
                                            <td>{city.publix_stores + city.competitor_stores}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'trends' && trendsData && (
                    <div className="trends-section">
                        <h3>Trends & Growth Analysis</h3>
                        <div className="trends-charts">
                            <div className="chart-container">
                                <h4>Store Openings Over Time</h4>
                                <ResponsiveContainer width="100%" height={400}>
                                    <LineChart data={trendsData.store_openings}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="year" />
                                        <YAxis />
                                        <Tooltip />
                                        <Legend />
                                        <Line
                                            type="monotone"
                                            dataKey="count"
                                            stroke="#0088FE"
                                            strokeWidth={2}
                                            name="Stores Opened"
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                            <div className="chart-container">
                                <h4>Predictions Over Time</h4>
                                <ResponsiveContainer width="100%" height={400}>
                                    <LineChart data={trendsData.predictions}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="year" />
                                        <YAxis yAxisId="left" />
                                        <YAxis yAxisId="right" orientation="right" />
                                        <Tooltip />
                                        <Legend />
                                        <Line
                                            yAxisId="left"
                                            type="monotone"
                                            dataKey="count"
                                            stroke="#00C49F"
                                            strokeWidth={2}
                                            name="Predictions Made"
                                        />
                                        <Line
                                            yAxisId="right"
                                            type="monotone"
                                            dataKey="avg_confidence"
                                            stroke="#FF8042"
                                            strokeWidth={2}
                                            name="Avg Confidence"
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'roi' && (
                    <div className="roi-section">
                        <h3>ROI Calculator</h3>
                        <div className="roi-inputs">
                            <div className="input-group">
                                <label>City:</label>
                                <input
                                    type="text"
                                    value={roiInputs.city}
                                    onChange={(e) =>
                                        setRoiInputs({ ...roiInputs, city: e.target.value })
                                    }
                                    placeholder="e.g., Miami"
                                />
                            </div>
                            <div className="input-group">
                                <label>State:</label>
                                <select
                                    value={roiInputs.state}
                                    onChange={(e) =>
                                        setRoiInputs({ ...roiInputs, state: e.target.value })
                                    }
                                >
                                    <option value="">Select State</option>
                                    <option value="FL">Florida</option>
                                    <option value="GA">Georgia</option>
                                    <option value="AL">Alabama</option>
                                    <option value="SC">South Carolina</option>
                                    <option value="NC">North Carolina</option>
                                    <option value="TN">Tennessee</option>
                                    <option value="VA">Virginia</option>
                                    <option value="KY">Kentucky</option>
                                </select>
                            </div>
                            <div className="input-group">
                                <label>Store Size (sq ft):</label>
                                <input
                                    type="number"
                                    value={roiInputs.estimated_store_size}
                                    onChange={(e) =>
                                        setRoiInputs({
                                            ...roiInputs,
                                            estimated_store_size: parseInt(e.target.value),
                                        })
                                    }
                                />
                            </div>
                            <div className="input-group">
                                <label>Land Cost per Acre:</label>
                                <input
                                    type="number"
                                    value={roiInputs.land_cost_per_acre}
                                    onChange={(e) =>
                                        setRoiInputs({
                                            ...roiInputs,
                                            land_cost_per_acre: parseFloat(e.target.value),
                                        })
                                    }
                                />
                            </div>
                            <div className="input-group">
                                <label>Construction Cost per sq ft:</label>
                                <input
                                    type="number"
                                    value={roiInputs.construction_cost_per_sqft}
                                    onChange={(e) =>
                                        setRoiInputs({
                                            ...roiInputs,
                                            construction_cost_per_sqft: parseFloat(e.target.value),
                                        })
                                    }
                                />
                            </div>
                            <button className="calculate-btn" onClick={handleRoiCalculate}>
                                Calculate ROI
                            </button>
                        </div>

                        {roiData && (
                            <div className="roi-results">
                                <h4>ROI Analysis for {roiData.city}, {roiData.state}</h4>
                                <div className="roi-cards">
                                    <div className="roi-card">
                                        <h5>Investment</h5>
                                        <p className="roi-value">
                                            ${roiData.costs.total_investment.toLocaleString()}
                                        </p>
                                        <div className="roi-details">
                                            <span>Land: ${roiData.costs.land_cost.toLocaleString()}</span>
                                            <span>
                                                Construction: ${roiData.costs.construction_cost.toLocaleString()}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="roi-card">
                                        <h5>Annual Revenue</h5>
                                        <p className="roi-value">
                                            ${roiData.revenue_estimate.annual_revenue.toLocaleString()}
                                        </p>
                                        <div className="roi-details">
                                            <span>
                                                Profit: ${roiData.revenue_estimate.annual_profit.toLocaleString()}
                                            </span>
                                            <span>
                                                Margin: {(roiData.revenue_estimate.profit_margin * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>
                                    <div className="roi-card highlight">
                                        <h5>ROI</h5>
                                        <p className="roi-value">{roiData.roi.roi_percentage}%</p>
                                        <div className="roi-details">
                                            <span>
                                                Payback: {roiData.roi.payback_years?.toFixed(1)} years
                                            </span>
                                            <span className={`recommendation ${roiData.recommendation}`}>
                                                {roiData.recommendation.toUpperCase()} OPPORTUNITY
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div className="roi-context">
                                    <h5>Market Context</h5>
                                    <div className="context-grid">
                                        <div>
                                            <strong>Population:</strong>{' '}
                                            {roiData.demographics.population?.toLocaleString()}
                                        </div>
                                        <div>
                                            <strong>Median Income:</strong>{' '}
                                            ${roiData.demographics.median_income?.toLocaleString()}
                                        </div>
                                        <div>
                                            <strong>Growth Rate:</strong>{' '}
                                            {roiData.demographics.growth_rate
                                                ? `${(roiData.demographics.growth_rate * 100).toFixed(2)}%`
                                                : 'N/A'}
                                        </div>
                                        <div>
                                            <strong>Existing Stores:</strong> {roiData.existing_stores}
                                        </div>
                                        <div>
                                            <strong>Available Parcels:</strong> {roiData.available_parcels}
                                        </div>
                                        {roiData.prediction_confidence && (
                                            <div>
                                                <strong>Prediction Confidence:</strong>{' '}
                                                {(roiData.prediction_confidence * 100).toFixed(1)}%
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

export default AdvancedAnalytics

