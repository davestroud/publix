import React, { useState } from 'react'
import './SearchBar.css'

function SearchBar({ filters, onFiltersChange }) {
    const [localFilters, setLocalFilters] = useState({
        state: filters.state || '',
        city: filters.city || '',
        min_confidence: filters.min_confidence || '',
    })

    const handleChange = (field, value) => {
        const newFilters = { ...localFilters, [field]: value }
        setLocalFilters(newFilters)
        onFiltersChange(newFilters)
    }

    const handleClear = () => {
        const cleared = { state: '', city: '', min_confidence: '' }
        setLocalFilters(cleared)
        onFiltersChange(cleared)
    }

    return (
        <div className="search-bar">
            <div className="search-fields">
                <div className="search-field">
                    <label>State</label>
                    <select
                        value={localFilters.state}
                        onChange={(e) => handleChange('state', e.target.value)}
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

                <div className="search-field">
                    <label>City</label>
                    <input
                        type="text"
                        placeholder="e.g., Miami, Owensboro"
                        value={localFilters.city}
                        onChange={(e) => handleChange('city', e.target.value)}
                    />
                </div>

                <div className="search-field">
                    <label>Min Confidence</label>
                    <input
                        type="number"
                        placeholder="0.0 - 1.0"
                        min="0"
                        max="1"
                        step="0.1"
                        value={localFilters.min_confidence}
                        onChange={(e) => handleChange('min_confidence', e.target.value)}
                    />
                </div>

                <button onClick={handleClear} className="clear-btn">
                    Clear Filters
                </button>
            </div>
        </div>
    )
}

export default SearchBar

