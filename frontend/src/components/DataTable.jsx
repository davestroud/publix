import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import './DataTable.css'

function DataTable({ filters = {}, type = 'predictions' }) {
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })

    useEffect(() => {
        loadData()
    }, [filters, type])

    const loadData = async () => {
        try {
            setLoading(true)
            let response
            if (type === 'predictions') {
                response = await api.getPredictions(filters)
            } else {
                response = await api.getStores(filters)
            }
            setData(response.data)
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
            if (a[key] < b[key]) return direction === 'asc' ? -1 : 1
            if (a[key] > b[key]) return direction === 'asc' ? 1 : -1
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
                return typeof value === 'string' ? `"${value}"` : value
            }).join(','))
        ].join('\n')

        const blob = new Blob([csv], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${type}_export.csv`
        a.click()
    }

    if (loading) {
        return <div className="loading">Loading data...</div>
    }

    if (error) {
        return <div className="error">{error}</div>
    }

    if (data.length === 0) {
        return <div className="loading">No data available</div>
    }

    const columns = type === 'predictions'
        ? ['city', 'state', 'confidence_score', 'reasoning', 'created_at']
        : ['city', 'state', 'address', 'square_feet', 'opening_date']

    return (
        <div className="data-table">
            <div className="table-header">
                <h2>{type === 'predictions' ? 'Predictions' : 'Stores'}</h2>
                <button onClick={exportToCSV} className="export-btn">
                    Export CSV
                </button>
            </div>

            <div className="table-container">
                <table>
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    onClick={() => handleSort(col)}
                                    className="sortable"
                                >
                                    {col.replace('_', ' ').toUpperCase()}
                                    {sortConfig.key === col && (
                                        <span>{sortConfig.direction === 'asc' ? ' ↑' : ' ↓'}</span>
                                    )}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, index) => (
                            <tr key={row.id || index}>
                                {columns.map((col) => (
                                    <td key={col}>
                                        {col === 'confidence_score'
                                            ? `${(row[col] * 100).toFixed(1)}%`
                                            : col === 'reasoning'
                                                ? row[col]?.substring(0, 100) + '...'
                                                : row[col]?.toString() || 'N/A'}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

export default DataTable

