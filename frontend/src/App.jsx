import React, { useState } from 'react'
import EnhancedDashboard from './components/EnhancedDashboard'
import MapView from './components/MapView'
import EnhancedDataTable from './components/EnhancedDataTable'
import SearchBar from './components/SearchBar'
import ReportViewer from './components/ReportViewer'
import PropertySearch from './components/PropertySearch'
import ChatInterface from './components/ChatInterface'
import AdvancedAnalytics from './components/AdvancedAnalytics'
import DataInsights from './components/DataInsights'
import './App.css'

function App() {
    const [activeView, setActiveView] = useState('dashboard')
    const [searchFilters, setSearchFilters] = useState({})

    return (
        <div className="app">
            <header className="app-header">
                <h1>Publix Expansion Predictor</h1>
                <nav className="nav-tabs">
                    <button
                        className={activeView === 'dashboard' ? 'active' : ''}
                        onClick={() => setActiveView('dashboard')}
                    >
                        Dashboard
                    </button>
                    <button
                        className={activeView === 'map' ? 'active' : ''}
                        onClick={() => setActiveView('map')}
                    >
                        Map
                    </button>
                    <button
                        className={activeView === 'table' ? 'active' : ''}
                        onClick={() => setActiveView('table')}
                    >
                        Data Table
                    </button>
                    <button
                        className={activeView === 'property' ? 'active' : ''}
                        onClick={() => setActiveView('property')}
                    >
                        Property Search
                    </button>
                    <button
                        className={activeView === 'chat' ? 'active' : ''}
                        onClick={() => setActiveView('chat')}
                    >
                        AI Assistant
                    </button>
                    <button
                        className={activeView === 'analytics' ? 'active' : ''}
                        onClick={() => setActiveView('analytics')}
                    >
                        Advanced Analytics
                    </button>
                    <button
                        className={activeView === 'reports' ? 'active' : ''}
                        onClick={() => setActiveView('reports')}
                    >
                        Reports
                    </button>
                    <button
                        className={activeView === 'insights' ? 'active' : ''}
                        onClick={() => setActiveView('insights')}
                    >
                        Data Insights
                    </button>
                </nav>
            </header>

            <div className="app-content">
                <SearchBar
                    filters={searchFilters}
                    onFiltersChange={setSearchFilters}
                />

                <main className="main-content">
                    {activeView === 'dashboard' && <EnhancedDashboard />}
                    {activeView === 'map' && <MapView filters={searchFilters} />}
                    {activeView === 'table' && <EnhancedDataTable filters={searchFilters} />}
                    {activeView === 'property' && <PropertySearch />}
                    {activeView === 'chat' && <ChatInterface />}
                    {activeView === 'analytics' && <AdvancedAnalytics />}
                    {activeView === 'reports' && <ReportViewer />}
                    {activeView === 'insights' && <DataInsights />}
                </main>
            </div>
        </div>
    )
}

export default App

