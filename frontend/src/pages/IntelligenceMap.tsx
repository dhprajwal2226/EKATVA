import { MapContainer, TileLayer, Popup, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import styles from './IntelligenceMap.module.css';

// Fix for default marker icons in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Mock locations for CPSE warehouses
const locations = [
  { id: 1, name: 'IOCL Panipat Refinery', lat: 29.3904, lng: 76.9701, type: 'refinery', cpse: 'IOCL', inventory: 15420 },
  { id: 2, name: 'NTPC Vindhyachal', lat: 24.0970, lng: 82.6375, type: 'powerplant', cpse: 'NTPC', inventory: 22100 },
  { id: 3, name: 'BHEL Haridwar', lat: 29.9457, lng: 78.1642, type: 'manufacturing', cpse: 'BHEL', inventory: 18500 },
  { id: 4, name: 'ONGC Mumbai High', lat: 19.4184, lng: 71.3005, type: 'offshore', cpse: 'ONGC', inventory: 9800 },
  { id: 5, name: 'GAIL Pata', lat: 26.6111, lng: 79.5700, type: 'petrochemical', cpse: 'GAIL', inventory: 11200 },
];

const IntelligenceMap = () => {
  const center: [number, number] = [22.9734, 78.6569]; // Center of India

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>National Intelligence Map</h1>
          <p className={styles.subtitle}>Geospatial view of material distribution, inventory levels, and inter-CPSE supply chain potential.</p>
        </div>
      </div>

      <div className={styles.mapContainer}>
        <div className={styles.mapInner}>
          <MapContainer center={center} zoom={5} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            />
            
            {locations.map((loc) => (
              <CircleMarker
                key={loc.id}
                center={[loc.lat, loc.lng]}
                radius={Math.max(8, loc.inventory / 1500)}
                fillColor="var(--color-primary)"
                color="white"
                weight={2}
                opacity={1}
                fillOpacity={0.7}
              >
                <Popup>
                  <div style={{ padding: '4px' }}>
                    <h3 style={{ margin: '0 0 4px 0', fontSize: '14px', color: 'var(--color-primary)' }}>{loc.name}</h3>
                    <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#64748b' }}>CPSE: <strong>{loc.cpse}</strong></p>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span>Inventory Items:</span>
                      <strong>{loc.inventory.toLocaleString()}</strong>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        <div className={styles.sidebar}>
          <h3 className={styles.sidebarTitle}>Material Landscape</h3>
          
          <div className={styles.statsGrid}>
            <div className={styles.statCard}>
              <div className={styles.statValue}>15</div>
              <div className={styles.statLabel}>CPSEs Mapped</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statValue}>3.2M</div>
              <div className={styles.statLabel}>Total SKU Value</div>
            </div>
          </div>

          <h4 className={styles.sectionTitle}>Key Distribution Hubs</h4>
          <div className={styles.locationList}>
            {locations.sort((a, b) => b.inventory - a.inventory).map(loc => (
              <div key={loc.id} className={styles.locationItem}>
                <div className={styles.locName}>{loc.name} ({loc.cpse})</div>
                <div className={styles.locDetails}>
                  <span>Inventory Volume</span>
                  <span>{loc.inventory.toLocaleString()} items</span>
                </div>
                <div className={styles.inventoryBar}>
                  <div 
                    className={styles.inventoryFill} 
                    style={{ width: `${(loc.inventory / 25000) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntelligenceMap;
