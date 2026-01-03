import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import './DataTable.css'

function EnhancedDataTable({ filters = {} }) {
    const [activeTab, setActiveTab] = useState('stores')
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
    const [searchTerm, setSearchTerm] = useState('')
    const [page, setPage] = useState(1)
    const [pageSize] = useState(50)

    useEffect(() => {
        loadData()
    }, [filters, activeTab, page])

    const loadData = async () => {
        try {
            setLoading(true)
            let response

            if (activeTab === 'stores') {
                response = await api.getStores({ ...filters, limit: 1000 })
            } else if (activeTab === 'competitors') {
                response = await api.getCompetitors({ ...filters, limit: 1000 })
            } else if (activeTab === 'demographics') {
                response = await api.getDemographicsList({ ...filters, limit: 1000 })
            } else if (activeTab === 'parcels') {
                response = await api.getParcels({ ...filters, limit: 1000 })
            } else {
                response = await api.getPredictions({ ...filters, limit: 1000 })
            }

            setData(response.data || [])
            setError(null)
        } catch (err) {
            setError('Failed to load data')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleSort = (key) => {
        let direction = 'asc'
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc'
        }
        setSortConfig({ key, direction })

        const sorted = [...data].sort((a, b) => {
            const aVal = a[key]
            const bVal = b[key]
            if (aVal === null || aVal === undefined) return 1
            if (bVal === null || bVal === undefined) return -1
            if (aVal < bVal) return direction === 'asc' ? -1 : 1
            if (aVal > bVal) return direction === 'asc' ? 1 : -1
            return 0
        })
        setData(sorted)
    }

    const exportToCSV = () => {
        if (data.length === 0) return

        const headers = Object.keys(data[0])
        const csv = [
            headers.join(','),
            ...data.map(row => headers.map(header => {
                const value = row[header]
                if (value === null || value === undefined) return ''
                return typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value
            }).join(','))
        ].join('\n')

        const blob = new Blob([csv], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${activeTab}_export.csv`
        a.click()
    }

    const filteredData = data.filter(item => {
        if (!searchTerm) return true
        const searchLower = searchTerm.toLowerCase()
        return Object.values(item).some(val =>
            val && val.toString().toLowerCase().includes(searchLower)
        )
    })

    const paginatedData = filteredData.slice((page - 1) * pageSize, page * pageSize)
    const totalPages = Math.ceil(filteredData.length / pageSize)

    const getColumns = () => {
        switch (activeTab) {
            case 'stores':
                return [
                    { key: 'store_number', label: 'Store #' },
                    { key: 'address', label: 'Address' },
                    { key: 'city', label: 'City' },
                    { key: 'state', label: 'State' },
                    { key: 'zip_code', label: 'Zip' },
                    { key: 'square_feet', label: 'Size (sq ft)' },
                ]
            case 'competitors':
                return [
                    { key: 'competitor_name', label: 'Competitor' },
                    { key: 'address', label: 'Address' },
                    { key: 'city', label: 'City' },
                    { key: 'state', label: 'State' },
                    { key: 'zip_code', label: 'Zip' },
                ]
            case 'demographics':
                return [
                    { key: 'city', label: 'City' },
                    { key: 'state', label: 'State' },
                    { key: 'population', label: 'Population' },
                    { key: 'median_income', label: 'Median Income' },
                    { key: 'median_age', label: 'Median Age' },
                    { key: 'growth_rate', label: 'Growth Rate' },
                    { key: 'data_year', label: 'Year' },
                ]
            case 'parcels':
                return [
                    { key: 'parcel_id', label: 'Parcel ID' },
                    { key: 'address', label: 'Address' },
                    { key: 'city', label: 'City' },
                    { key: 'state', label: 'State' },
                    { key: 'acreage', label: 'Acreage' },
                    { key: 'current_zoning', label: 'Zoning' },
                    { key: 'assessed_value', label: 'Assessed Value' },
                    { key: 'owner_name', label: 'Owner' },
                ]
            case 'predictions':
                return [
                    { key: 'city', label: 'City' },
                    { key: 'state', label: 'State' },
                    { key: 'confidence_score', label: 'Confidence' },
                    { key: 'reasoning', label: 'Reasoning' },
                    { key: 'created_at', label: 'Created' },
                ]
            default:
                return []
        }
    }

    const formatValue = (value, key) => {
        if (value === null || value === undefined) return 'N/A'
        if (key === 'confidence_score') return `${(value * 100).toFixed(1)}%`
        if (key === 'reasoning') return value.substring(0, 100) + (value.length > 100 ? '...' : '')
        if (key === 'square_feet' && value) return value.toLocaleString()
        if (key === 'population' && value) return value.toLocaleString()
        if (key === 'median_income' && value) return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
        if (key === 'assessed_value' && value) return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
        if (key === 'acreage' && value) return `${value.toFixed(2)} acres`
        if (key === 'growth_rate' && value) return `${(value * 100).toFixed(2)}%`
        if (key === 'created_at' && typeof value === 'string') {
            return new Date(value).toLocaleDateString()
        }
        return value.toString()
    }

    if (loading) {
        return <div className="loading">Loading data...</div>
    }

    if (error) {
        return <div className="error">{error}</div>
    }

    const columns = getColumns()

    return (
        <div className="data-table">
            <div className="table-header">
                <div className="tabs">
                    <button
                        className={activeTab === 'stores' ? 'active' : ''}
                        onClick={() => { setActiveTab('stores'); setPage(1); }}
                    >
                        Publix Stores ({data.length})
                    </button>
                    <button
                        className={activeTab === 'competitors' ? 'active' : ''}
                        onClick={() => { setActiveTab('competitors'); setPage(1); }}
                    >
                        Competitors ({data.length})
                    </button>
                    <button
                        className={activeTab === 'demographics' ? 'active' : ''}
                        onClick={() => { setActiveTab('demographics'); setPage(1); }}
                    >
                        Demographics ({data.length})
                    </button>
                    <button
                        className={activeTab === 'parcels' ? 'active' : ''}
                        onClick={() => { setActiveTab('parcels'); setPage(1); }}
                    >
                        Parcels ({data.length})
                    </button>
                    <button
                        className={activeTab === 'predictions' ? 'active' : ''}
                        onClick={() => { setActiveTab('predictions'); setPage(1); }}
                    >
                        Predictions ({data.length})
                    </button>
                </div>
                <div className="table-actions">
                    <input
                        type="text"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
                        className="search-input"
                    />
                    <button onClick={exportToCSV} className="export-btn">
                        Export CSV
                    </button>
                </div>
            </div>

            <div className="table-info">
                Showing {paginatedData.length} of {filteredData.length} {activeTab}
                {filteredData.length !== data.length && ` (filtered from ${data.length} total)`}
            </div>

            <div className="table-container">
                <table>
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col.key}
                                    onClick={() => handleSort(col.key)}
                                    className="sortable"
                                >
                                    {col.label}
                                    {sortConfig.key === col.key && (
                                        <span>{sortConfig.direction === 'asc' ? ' ↑' : ' ↓'}</span>
                                    )}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {paginatedData.length === 0 ? (
                            <tr>
                                <td colSpan={columns.length} className="no-data">
                                    No data available
                                </td>
                            </tr>
                        ) : (
                            paginatedData.map((row, index) => (
                                <tr key={row.id || index}>
                                    {columns.map((col) => (
                                        <td key={col.key}>
                                            {formatValue(row[col.key], col.key)}
                                        </td>
                                    ))}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {totalPages > 1 && (
                <div className="pagination">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                    >
                        Previous
                    </button>
                    <span>Page {page} of {totalPages}</span>
                    <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    )
}

export default EnhancedDataTable

