import React, { useState } from 'react'
import { api } from '../services/api'
import './PropertySearch.css'

function PropertySearch() {
    const [formData, setFormData] = useState({
        address: '',
        city: '',
        state: '',
        zipCode: '',
    })
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        })
    }

    const handleGeocode = async () => {
        if (!formData.address || !formData.city || !formData.state) {
            setError('Please fill in address, city, and state')
            return
        }

        setLoading(true)
        setError(null)
        setResult(null)

        try {
            const response = await api.geocodeAddress(
                formData.address,
                formData.city,
                formData.state,
                formData.zipCode || undefined
            )
            setResult({ type: 'geocode', data: response.data })
        } catch (err) {
            setError(err.response?.data?.detail || 'Geocoding failed')
        } finally {
            setLoading(false)
        }
    }

    const handlePropertyLookup = async () => {
        if (!formData.address || !formData.city || !formData.state) {
            setError('Please fill in address, city, and state')
            return
        }

        setLoading(true)
        setError(null)
        setResult(null)

        try {
            const response = await api.getPropertyData(
                formData.address,
                formData.city,
                formData.state,
                formData.zipCode || undefined
            )
            setResult({ type: 'property', data: response.data })
        } catch (err) {
            setError(err.response?.data?.detail || 'Property lookup failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="property-search">
            <h2>Smarty Property Search</h2>
            <div className="search-form">
                <div className="form-row">
                    <div className="form-group">
                        <label>Address</label>
                        <input
                            type="text"
                            name="address"
                            value={formData.address}
                            onChange={handleChange}
                            placeholder="123 Main St"
                        />
                    </div>
                    <div className="form-group">
                        <label>City</label>
                        <input
                            type="text"
                            name="city"
                            value={formData.city}
                            onChange={handleChange}
                            placeholder="Lexington"
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label>State</label>
                        <input
                            type="text"
                            name="state"
                            value={formData.state}
                            onChange={handleChange}
                            placeholder="KY"
                            maxLength="2"
                        />
                    </div>
                    <div className="form-group">
                        <label>ZIP Code (Optional)</label>
                        <input
                            type="text"
                            name="zipCode"
                            value={formData.zipCode}
                            onChange={handleChange}
                            placeholder="40508"
                        />
                    </div>
                </div>
                <div className="form-actions">
                    <button
                        onClick={handleGeocode}
                        disabled={loading}
                        className="btn btn-primary"
                    >
                        {loading ? 'Geocoding...' : 'Geocode Address'}
                    </button>
                    <button
                        onClick={handlePropertyLookup}
                        disabled={loading}
                        className="btn btn-secondary"
                    >
                        {loading ? 'Looking up...' : 'Get Property Data'}
                    </button>
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            {result && (
                <div className="result-panel">
                    <h3>
                        {result.type === 'geocode' ? 'Geocoding Result' : 'Property Data'}
                    </h3>
                    {result.type === 'geocode' && (
                        <div className="result-content">
                            <div className="result-item">
                                <strong>Address:</strong> {result.data.address}
                            </div>
                            <div className="result-item">
                                <strong>City:</strong> {result.data.city}
                            </div>
                            <div className="result-item">
                                <strong>State:</strong> {result.data.state}
                            </div>
                            <div className="result-item">
                                <strong>ZIP Code:</strong> {result.data.zip_code}
                            </div>
                            {result.data.latitude && result.data.longitude && (
                                <div className="result-item">
                                    <strong>Coordinates:</strong>{' '}
                                    {result.data.latitude.toFixed(6)}, {result.data.longitude.toFixed(6)}
                                </div>
                            )}
                            {result.data.precision && (
                                <div className="result-item">
                                    <strong>Precision:</strong> {result.data.precision}
                                </div>
                            )}
                        </div>
                    )}
                    {result.type === 'property' && (
                        <div className="result-content">
                            <div className="result-item">
                                <strong>Address:</strong> {result.data.address}
                            </div>
                            {result.data.latitude && result.data.longitude && (
                                <div className="result-item">
                                    <strong>Coordinates:</strong>{' '}
                                    {result.data.latitude.toFixed(6)}, {result.data.longitude.toFixed(6)}
                                </div>
                            )}
                            {result.data.property_data && (
                                <div className="property-details">
                                    <h4>Property Details</h4>
                                    <pre>{JSON.stringify(result.data.property_data, null, 2)}</pre>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

export default PropertySearch

