import { useState } from 'react';
import { Fingerprint, Search, AlertCircle, Loader2 } from 'lucide-react';
import styles from './MaterialDNA.module.css';
import { dnaService } from '../services/dna';
import type { MaterialDNAResponse } from '../types/api';

const MaterialDNA = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [dnaResult, setDnaResult] = useState<MaterialDNAResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchTerm.trim()) return;

    const materialId = parseInt(searchTerm.trim(), 10);
    if (isNaN(materialId)) {
      setError('Material ID must be an integer.');
      return;
    }

    setLoading(true);
    setError(null);
    setNotFound(false);
    setDnaResult(null);

    try {
      const data = await dnaService.getMaterialDNA(materialId);
      setDnaResult(data);
    } catch (err: any) {
      if (err.status === 404) {
        setNotFound(true);
      } else {
        setError(err.message || 'Failed to fetch material DNA.');
      }
    } finally {
      setLoading(false);
    }
  };

  const renderDnaGrid = () => {
    if (!dnaResult) return null;

    const attrs = dnaResult.attributes;
    const items = [
      { label: 'Material Type', value: attrs.material_type, key: 'material_type' },
      { label: 'Material', value: attrs.material, key: 'material' },
      { label: 'Grade', value: attrs.grade, key: 'grade' },
      { label: 'Size', value: attrs.size, key: 'size' },
      { label: 'Diameter', value: attrs.diameter, key: 'diameter' },
      { label: 'Length', value: attrs.length, key: 'length' },
      { label: 'Width', value: attrs.width, key: 'width' },
      { label: 'Height', value: attrs.height, key: 'height' },
      { label: 'Thickness', value: attrs.thickness, key: 'thickness' },
      { label: 'Pressure', value: attrs.pressure, key: 'pressure' },
      { label: 'Schedule', value: attrs.schedule, key: 'schedule' },
      { label: 'Form', value: attrs.form, key: 'form' },
      { label: 'Standard', value: attrs.standard, key: 'standard' },
      { label: 'Application', value: attrs.application, key: 'application' },
      { label: 'Manufacturer', value: attrs.manufacturer, key: 'manufacturer' },
    ].filter(item => item.value !== null && item.value !== undefined);

    if (items.length === 0) {
      return <div style={{ color: '#64748b' }}>No extracted attributes available.</div>;
    }

    return (
      <div className={styles.dnaGrid}>
        {items.map(item => {
          const conf = attrs.confidence_scores?.[item.key] || dnaResult.overall_confidence || 0;
          return (
            <div className={styles.dnaNode} key={item.key}>
              <span className={styles.nodeLabel}>{item.label}</span>
              <span className={styles.nodeValue}>{String(item.value).toUpperCase()}</span>
              {conf > 0 && (
                <div className={styles.confidenceBadge}>{Math.round(conf * 100)}%</div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>Material DNA</h1>
          <p className={styles.subtitle}>Convert unstructured material descriptions into a technical material fingerprint.</p>
        </div>
        <form onSubmit={handleSearch} className={styles.searchBar}>
          <input 
            type="text" 
            placeholder="Enter Material ID..." 
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
          <h3 style={{ margin: '0 0 8px 0', color: '#334155' }}>DNA not extracted</h3>
          <p style={{ margin: 0, color: '#64748b' }}>The requested material DNA is not available.</p>
        </div>
      )}

      {dnaResult && (
        <div className={styles.mainCard}>
          <div className={styles.sourceSection}>
            <h2 className={styles.sectionTitle}>Source Description</h2>
            <div className={styles.sourceDescriptions}>
              <div className={styles.sourceRow}>
                <span className={styles.cpseTag}>{dnaResult.material_code}</span>
                <span className={styles.sourceText}>{dnaResult.original_description}</span>
              </div>
              {dnaResult.normalized_description && dnaResult.normalized_description !== dnaResult.original_description && (
                <div className={styles.sourceRow} style={{ marginTop: '8px' }}>
                  <span className={styles.cpseTag} style={{ backgroundColor: '#64748b' }}>NORM</span>
                  <span className={styles.sourceText}>{dnaResult.normalized_description}</span>
                </div>
              )}
            </div>
          </div>

          <div className={styles.visualizationArea}>
            <div className={styles.fingerprintHeader}>
              <Fingerprint className={styles.fingerprintIcon} />
              <h2 className={styles.title} style={{ fontSize: '1.25rem' }}>Technical Fingerprint</h2>
            </div>
            
            {renderDnaGrid()}
          </div>
        </div>
      )}
    </div>
  );
};

export default MaterialDNA;
