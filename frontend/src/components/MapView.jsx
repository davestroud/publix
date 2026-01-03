import React, { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { api } from '../services/api'
import L from 'leaflet'
import './MapView.css'

// Fix for default marker icons in React Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

function MapView({ filters = {} }) {
    const [stores, setStores] = useState([])
    const [predictions, setPredictions] = useState([])
    const [parcels, setParcels] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [showStores, setShowStores] = useState(true)
    const [showPredictions, setShowPredictions] = useState(true)
    const [showParcels, setShowParcels] = useState(true)

    useEffect(() => {
        loadMapData()
    }, [filters])

    const loadMapData = async () => {
        try {
            setLoading(true)
            const [storesRes, predictionsRes, parcelsRes] = await Promise.all([
                api.getStores(filters),
                api.getPredictions(filters),
                api.getParcels(filters).catch(() => ({ data: [] })) // Parcels optional
            ])
            setStores(storesRes.data)
            setPredictions(predictionsRes.data)
            setParcels(parcelsRes.data || [])
            setError(null)
        } catch (err) {
            setError('Failed to load map data')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return <div className="loading">Loading map...</div>
    }

    if (error) {
        return <div className="error">{error}</div>
    }

    // Default center - prioritize parcels, then stores, then US center
    const center = parcels.length > 0 && parcels[0].latitude
        ? [parcels[0].latitude, parcels[0].longitude]
        : stores.length > 0 && stores[0].latitude
            ? [stores[0].latitude, stores[0].longitude]
            : [39.8283, -98.5795]

    return (
        <div className="map-view">
            <div className="map-controls">
                <label>
                    <input
                        type="checkbox"
                        checked={showStores}
                        onChange={(e) => setShowStores(e.target.checked)}
                    />
                    Show Current Stores ({stores.length})
                </label>
                <label>
                    <input
                        type="checkbox"
                        checked={showPredictions}
                        onChange={(e) => setShowPredictions(e.target.checked)}
                    />
                    Show Predictions ({predictions.length})
                </label>
                <label>
                    <input
                        type="checkbox"
                        checked={showParcels}
                        onChange={(e) => setShowParcels(e.target.checked)}
                    />
                    Show Parcels ({parcels.length})
                </label>
            </div>

            <div className="map-container">
                <MapContainer
                    center={center}
                    zoom={6}
                    style={{ height: '600px', width: '100%' }}
                >
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />

                    {showStores && stores.map((store) => (
                        store.latitude && store.longitude && (
                            <Marker
                                key={store.id}
                                position={[store.latitude, store.longitude]}
                            >
                                <Popup>
                                    <div>
                                        <h4>Publix Store</h4>
                                        <p>{store.address}</p>
                                        <p>{store.city}, {store.state}</p>
                                        {store.square_feet && <p>Size: {store.square_feet.toLocaleString()} sq ft</p>}
                                    </div>
                                </Popup>
                            </Marker>
                        )
                    ))}

                    {showPredictions && predictions.map((pred) => (
                        pred.latitude && pred.longitude && (
                            <Marker
                                key={pred.id}
                                position={[pred.latitude, pred.longitude]}
                                icon={L.icon({
                                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
                                    iconSize: [25, 41],
                                    iconAnchor: [12, 41],
                                })}
                            >
                                <Popup>
                                    <div>
                                        <h4>Predicted Location</h4>
                                        <p>{pred.city}, {pred.state}</p>
                                        <p>Confidence: {(pred.confidence_score * 100).toFixed(1)}%</p>
                                        <p>{pred.reasoning}</p>
                                    </div>
                                </Popup>
                            </Marker>
                        )
                    ))}

                    {showParcels && parcels.map((parcel) => (
                        parcel.latitude && parcel.longitude && (
                            <Marker
                                key={parcel.id || parcel.parcel_id}
                                position={[parcel.latitude, parcel.longitude]}
                                icon={L.icon({
                                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                                    iconSize: [25, 41],
                                    iconAnchor: [12, 41],
                                })}
                            >
                                <Popup>
                                    <div>
                                        <h4>Parcel</h4>
                                        {parcel.parcel_id && <p><strong>Parcel ID:</strong> {parcel.parcel_id}</p>}
                                        {parcel.address && <p><strong>Address:</strong> {parcel.address}</p>}
                                        <p>{parcel.city}, {parcel.state}</p>
                                        {parcel.acreage && <p><strong>Acreage:</strong> {parcel.acreage.toFixed(2)} acres</p>}
                                        {parcel.current_zoning && <p><strong>Zoning:</strong> {parcel.current_zoning}</p>}
                                        {parcel.assessed_value && <p><strong>Assessed Value:</strong> ${parcel.assessed_value.toLocaleString()}</p>}
                                        {parcel.owner_name && <p><strong>Owner:</strong> {parcel.owner_name}</p>}
                                    </div>
                                </Popup>
                            </Marker>
                        )
                    ))}
                </MapContainer>
            </div>
        </div>
    )
}

export default MapView

