import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { AlertCircle } from 'lucide-react';
import styles from './IntelligenceMap.module.css';

// Fix for default marker icons in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

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
          </MapContainer>
          
          <div className={styles.emptyOverlay}>
            <div className={styles.emptyBox}>
              <AlertCircle className={styles.emptyIcon} />
              <h2>No location data available in the database.</h2>
              <p>The backend does not currently track geocoded coordinates (latitude/longitude) for CPSEs, vendors, or materials. Displaying empty base map.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntelligenceMap;
