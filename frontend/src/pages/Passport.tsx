import { useState } from 'react';
import { Fingerprint, Search, Factory, AlertCircle, Loader2, BarChart2, Zap, TrendingUp } from 'lucide-react';
import styles from './Passport.module.css';
import { passportService } from '../services/passport';
import type { MaterialPassportResponse } from '../types/api';

const Passport = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [passport, setPassport] = useState<MaterialPassportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    setError(null);
    setNotFound(false);
    setPassport(null);

    try {
      const data = await passportService.getPassport(searchTerm.trim());
      setPassport(data);
    } catch (err: any) {
      if (err.status === 404) {
        setNotFound(true);
      } else {
        setError(err.message || 'Failed to fetch material passport.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>Material Passport</h1>
          <p className={styles.subtitle}>Trace origin, technical specifications, and network metrics of standardized materials.</p>
        </div>
        <form onSubmit={handleSearch} className={styles.searchBar}>
          <input 
            type="text" 
            placeholder="Enter CNMC..." 
            className={styles.searchInput} 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="submit" className={styles.searchBtn} disabled={loading}>
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Search size={18} />}
          </button>
        </form>
      </div>

      {loading && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px', color: '#64748b' }}>
          <Loader2 size={32} className="animate-spin" />
        </div>
      )}

      {error && (
        <div style={{ padding: '16px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '8px', marginTop: '24px' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {notFound && (
        <div style={{ padding: '40px', textAlign: 'center', background: '#f8fafc', border: '1px dashed #cbd5e1', borderRadius: '12px', marginTop: '24px' }}>
          <Search size={48} color="#94a3b8" style={{ margin: '0 auto 16px auto' }} />
          <h3 style={{ margin: '0 0 8px 0', color: '#334155' }}>Material passport not available</h3>
          <p style={{ margin: 0, color: '#64748b' }}>No verified passport could be found for the specified CNMC.</p>
        </div>
      )}

      {passport && (
        <div className={styles.passportCard}>
          <div className={styles.passportHeader}>
            <div>
              <div className={styles.passportId}>{passport.cnmc}</div>
              <div className={styles.passportDesc}>{passport.identity.description}</div>
              <div style={{ marginTop: '8px', display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 10px', background: 'rgba(255,255,255,0.2)', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 600 }}>
                {passport.identity.category}
              </div>
            </div>
            <div className={styles.qrCode}>
              <div style={{ width: '80%', height: '80%', backgroundImage: 'repeating-linear-gradient(45deg, #0f172a 0, #0f172a 10%, transparent 10%, transparent 20%)' }}></div>
            </div>
          </div>

          <div className={styles.passportBody}>
            <div>
              <div className={styles.section}>
                <h3 className={styles.sectionTitle}><Fingerprint size={18} /> Technical Specifications</h3>
                <div className={styles.detailsGrid}>
                  {Object.entries(passport.technical_attributes).map(([key, value]) => (
                    <div className={styles.detailItem} key={key}>
                      <span className={styles.detailLabel} style={{ textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}</span>
                      <span className={styles.detailValue}>{String(value)}</span>
                    </div>
                  ))}
                  {Object.keys(passport.technical_attributes).length === 0 && (
                    <div className={styles.detailItem}>
                      <span className={styles.detailValue}>No technical attributes available.</span>
                    </div>
                  )}
                </div>
              </div>

              {passport.cpse_mappings && passport.cpse_mappings.length > 0 && (
                <div className={styles.section}>
                  <h3 className={styles.sectionTitle}><Factory size={18} /> CPSE Mappings</h3>
                  <div className={styles.detailsGrid}>
                    {passport.cpse_mappings.map((mapping, idx) => (
                      <div className={styles.detailItem} key={idx}>
                        <span className={styles.detailLabel}>{mapping.cpse}</span>
                        <span className={styles.detailValue}>{mapping.code}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div>
              <div className={styles.section}>
                <h3 className={styles.sectionTitle}><BarChart2 size={18} /> Supply & Demand Network</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600, marginBottom: '8px' }}>Supply Metrics</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Available Inventory</div>
                        <div style={{ fontWeight: 600, color: '#0f172a' }}>{passport.supply.available.toLocaleString()}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Total Inventory</div>
                        <div style={{ fontWeight: 600, color: '#0f172a' }}>{passport.supply.inventory.toLocaleString()}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Reserved</div>
                        <div style={{ fontWeight: 600, color: '#0f172a' }}>{passport.supply.reserved.toLocaleString()}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Vendors</div>
                        <div style={{ fontWeight: 600, color: '#0f172a' }}>{passport.supply.vendor_count}</div>
                      </div>
                    </div>
                  </div>

                  <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600, marginBottom: '8px' }}>Demand Metrics</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Current Demand</div>
                        <div style={{ fontWeight: 600, color: '#0f172a' }}>{passport.demand.current.toLocaleString()}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Forecast Demand</div>
                        <div style={{ fontWeight: 600, color: '#0f172a' }}>{passport.demand.forecast.toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className={styles.section}>
                <h3 className={styles.sectionTitle}><Zap size={18} /> Network Intelligence</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px', borderRadius: '8px', background: passport.intelligence.signal === 'BUY' ? '#f0fdf4' : passport.intelligence.signal === 'HOLD' ? '#fffbeb' : '#fef2f2', border: `1px solid ${passport.intelligence.signal === 'BUY' ? '#bbf7d0' : passport.intelligence.signal === 'HOLD' ? '#fde68a' : '#fecaca'}` }}>
                    <TrendingUp size={20} color={passport.intelligence.signal === 'BUY' ? '#166534' : passport.intelligence.signal === 'HOLD' ? '#b45309' : '#991b1b'} />
                    <div>
                      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: passport.intelligence.signal === 'BUY' ? '#166534' : passport.intelligence.signal === 'HOLD' ? '#b45309' : '#991b1b' }}>Market Signal: {passport.intelligence.signal}</div>
                      {(passport.intelligence.potential_gap !== null || passport.intelligence.potential_surplus !== null) && (
                        <div style={{ fontSize: '0.75rem', color: passport.intelligence.signal === 'BUY' ? '#15803d' : passport.intelligence.signal === 'HOLD' ? '#d97706' : '#b91c1c' }}>
                          {passport.intelligence.potential_gap ? `Potential Gap: ${passport.intelligence.potential_gap}` : ''}
                          {passport.intelligence.potential_surplus ? `Potential Surplus: ${passport.intelligence.potential_surplus}` : ''}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', textAlign: 'center' }}>
                    <div style={{ padding: '8px', background: '#f1f5f9', borderRadius: '6px' }}>
                      <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#334155' }}>{passport.graph_summary.cpse_count}</div>
                      <div style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>CPSEs</div>
                    </div>
                    <div style={{ padding: '8px', background: '#f1f5f9', borderRadius: '6px' }}>
                      <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#334155' }}>{passport.graph_summary.vendor_count}</div>
                      <div style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>Vendors</div>
                    </div>
                    <div style={{ padding: '8px', background: '#f1f5f9', borderRadius: '6px' }}>
                      <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#334155' }}>{passport.graph_summary.location_count}</div>
                      <div style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>Locations</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Passport;
