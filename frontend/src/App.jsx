import { useState } from 'react';
import './App.css';
import MapComponent from './components/MapComponent';

function App() {
    const [terms, setTerms] = useState('cafe, restaurant');
    const [location, setLocation] = useState('Soho, London');
    const [enrich, setEnrich] = useState(false);
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSearch = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResults([]);

        try {
            const termList = terms.split(',').map(t => t.trim()).filter(t => t);
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    terms: termList,
                    location: location,
                    enrich: enrich
                })
            });

            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data = await response.json();
            setResults(data.results || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadCSV = () => {
        if (!results.length) return;

        // Define headers
        const headers = ['Name', 'Category', 'Phone', 'Website', 'Address Street', 'Address City', 'OSM ID'];

        // Convert to CSV string
        const csvContent = [
            headers.join(','),
            ...results.map(r => [
                `"${(r.name || '').replace(/"/g, '""')}"`,
                `"${(r.category || '').replace(/"/g, '""')}"`,
                `"${(r.phone || '').replace(/"/g, '""')}"`,
                `"${(r.website || '').replace(/"/g, '""')}"`,
                `"${(r.address_street || '').replace(/"/g, '""')}"`,
                `"${(r.address_city || '').replace(/"/g, '""')}"`,
                r.osm_id
            ].join(','))
        ].join('\n');

        // Create blob and download link
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', 'results.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    return (
        <div className="container">
            <header className="header">
                <h1>FindPlace <span className="highlight">Scraper</span></h1>
                <p>Expert business lead generation from OpenStreetMap</p>
            </header>

            <div className="search-section glass-panel">
                <form onSubmit={handleSearch} className="search-form">
                    <div className="form-group">
                        <label>Search Terms</label>
                        <input
                            type="text"
                            value={terms}
                            onChange={(e) => setTerms(e.target.value)}
                            placeholder="e.g. cafe, gym, bakery"
                        />
                    </div>
                    <div className="form-group">
                        <label>Location</label>
                        <input
                            type="text"
                            value={location}
                            onChange={(e) => setLocation(e.target.value)}
                            placeholder="e.g. New York City"
                        />
                    </div>
                    <div className="form-group checkbox-group">
                        <label className="toggle-label">
                            <input
                                type="checkbox"
                                checked={enrich}
                                onChange={(e) => setEnrich(e.target.checked)}
                            />
                            <span className="checkbox-custom"></span>
                            Enrich Data (Crawl Websites)
                        </label>
                    </div>
                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Searching...' : 'Find Businesses'}
                    </button>
                </form>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="results-container">
                {results.length > 0 && (
                    <div className="split-view">
                        <div className="list-view glass-panel">
                            <div className="results-header">
                                <h3>Results ({results.length})</h3>
                                <button onClick={handleDownloadCSV} className="btn-secondary">
                                    Download CSV
                                </button>
                            </div>
                            <div className="results-list">
                                {results.map((r) => (
                                    <div key={r.osm_id} className="result-card">
                                        <h4>{r.name}</h4>
                                        <div className="tags">
                                            <span className="tag-category">{r.category}</span>
                                        </div>
                                        <p className="address">{r.address_street}, {r.address_city}</p>
                                        {r.website && <a href={r.website} target="_blank" rel="noreferrer" className="link">Website</a>}
                                        {r.phone && <div className="phone">📞 {r.phone}</div>}
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="map-view">
                            <MapComponent businesses={results} />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
