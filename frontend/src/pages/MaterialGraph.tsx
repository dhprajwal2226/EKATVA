import { useState } from 'react';
import { Search, Loader2, AlertCircle, Info, Database, Users, MapPin } from 'lucide-react';
import styles from './MaterialGraph.module.css';
import { passportService } from '../services/passport';
import type { MaterialPassportResponse } from '../types/api';

const MaterialGraph = () => {
  const [cnmc, setCnmc] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [passport, setPassport] = useState<MaterialPassportResponse | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cnmc.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await passportService.getPassport(cnmc);
      setPassport(data);
    } catch (err: any) {
      setError(err.message || 'Material not found or no graph summary available.');
      setPassport(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>Material Knowledge Graph</h1>
          <p className={styles.subtitle}>Explore relationships between National Masters, CPSE codes, and material attributes.</p>
        </div>
      </div>

      <div className={styles.card}>
        <form onSubmit={handleSearch} className={styles.searchForm}>
          <div className={styles.inputGroup}>
            <Search className={styles.searchIcon} />
            <input
              type="text"
              value={cnmc}
              onChange={(e) => setCnmc(e.target.value)}
              placeholder="Enter CNMC (e.g., CNMC-000001)..."
              className={styles.searchInput}
              disabled={loading}
            />
            <button 
              type="submit" 
              className={styles.searchButton}
              disabled={loading || !cnmc.trim()}
            >
              {loading ? <Loader2 className={styles.spinner} /> : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className={styles.errorBox}>
            <AlertCircle className={styles.errorIcon} />
            <span>{error}</span>
          </div>
        )}

        {passport ? (
          <div className={styles.resultsContainer}>
            <div className={styles.infoBanner}>
              <Info className={styles.infoIcon} />
              <p>Detailed node/edge relationship data is not available in the current database schema. Displaying graph summary metrics instead.</p>
            </div>
            
            <div className={styles.summaryGrid}>
              <div className={styles.summaryCard}>
                <div className={styles.summaryIconWrapper + ' ' + styles.bgPrimary}>
                  <Database className={styles.summaryIcon} />
                </div>
                <div className={styles.summaryContent}>
                  <div className={styles.summaryLabel}>Associated CPSEs</div>
                  <div className={styles.summaryValue}>{passport.graph_summary.cpse_count}</div>
                </div>
              </div>

              <div className={styles.summaryCard}>
                <div className={styles.summaryIconWrapper + ' ' + styles.bgSuccess}>
                  <Users className={styles.summaryIcon} />
                </div>
                <div className={styles.summaryContent}>
                  <div className={styles.summaryLabel}>Total Vendors</div>
                  <div className={styles.summaryValue}>{passport.graph_summary.vendor_count}</div>
                </div>
              </div>

              <div className={styles.summaryCard}>
                <div className={styles.summaryIconWrapper + ' ' + styles.bgAccent}>
                  <MapPin className={styles.summaryIcon} />
                </div>
                <div className={styles.summaryContent}>
                  <div className={styles.summaryLabel}>Stock Locations</div>
                  <div className={styles.summaryValue}>{passport.graph_summary.location_count}</div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          !error && (
            <div className={styles.emptyState}>
              <p>Enter a Material ID (CNMC) to view graph relationship metrics.</p>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default MaterialGraph;
