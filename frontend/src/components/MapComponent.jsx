import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useEffect, useState } from 'react';

const MapComponent = ({ businesses, center }) => {
    const [mapCenter, setMapCenter] = useState([51.505, -0.09]);

    useEffect(() => {
        if (center && center.lat && center.lon) {
            setMapCenter([center.lat, center.lon]);
        } else if (businesses.length > 0) {
            setMapCenter([businesses[0].lat, businesses[0].lon]);
        }
    }, [center, businesses]);

    return (
        <div className="glass-panel" style={{ height: '500px', width: '100%', overflow: 'hidden' }}>
            <MapContainer
                center={mapCenter}
                zoom={13}
                style={{ height: '100%', width: '100%' }}
                key={mapCenter.join(',')} // Force re-render on center change
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {businesses.map((b) => (
                    b.lat && b.lon ? (
                        <Marker key={b.osm_id} position={[b.lat, b.lon]}>
                            <Popup>
                                <strong>{b.name}</strong><br />
                                {b.category}<br />
                                {b.address_street}
                            </Popup>
                        </Marker>
                    ) : null
                ))}
            </MapContainer>
        </div>
    );
};

export default MapComponent;
