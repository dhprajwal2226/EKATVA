import { useState } from 'react';
import { ArrowRight, Search, Loader2, AlertCircle } from 'lucide-react';
import styles from './Normalization.module.css';
import { normalizationService } from '../services/normalization';
import type { NormalizeResponse } from '../types/api';

const Normalization = () => {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<NormalizeResponse | null>(null);

  const handleNormalize = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await normalizationService.normalizeText(inputText);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to normalize text. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Data Normalization</h1>
        <p className={styles.subtitle}>Standardize terminology, handle unit conversions, and correct formatting before AI matching.</p>
      </div>

      <div className={styles.card}>
        <form onSubmit={handleNormalize} className={styles.searchForm}>
          <div className={styles.inputGroup}>
            <Search className={styles.searchIcon} />
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter raw material description (e.g., SS BOLT M16 X 50MM)..."
              className={styles.searchInput}
              disabled={loading}
            />
            <button 
              type="submit" 
              className={styles.searchButton}
              disabled={loading || !inputText.trim()}
            >
              {loading ? <Loader2 className={styles.spinner} /> : 'Normalize'}
            </button>
          </div>
        </form>

        {error && (
          <div className={styles.errorBox}>
            <AlertCircle className={styles.errorIcon} />
            <span>{error}</span>
          </div>
        )}

        {result ? (
          <>
            <div className={styles.comparisonSection}>
              <div className={styles.valueBox}>
                <div className={styles.valueLabel}>Original Input</div>
                <div className={styles.valueText}>{result.original_description}</div>
              </div>
              
              <div className={styles.arrow}>
                <ArrowRight />
              </div>
              
              <div className={styles.valueBox + ' ' + styles.normalized}>
                <div className={styles.valueLabel}>Normalized Output</div>
                <div className={styles.valueText}>{result.normalized_description}</div>
              </div>
            </div>

            {result.expanded_abbreviations.length > 0 && (
              <>
                <h2 className={styles.sectionTitle}>Applied Transformations</h2>
                <table className={styles.transformTable}>
                  <thead>
                    <tr>
                      <th>Original Term</th>
                      <th>Expanded Term</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.expanded_abbreviations.map((item, index) => (
                      <tr key={index}>
                        <td><span className={styles.originalText}>{item.abbr}</span></td>
                        <td><span className={styles.newText}>{item.expansion}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            )}

            {result.dimensions.length > 0 && (
              <div style={{ marginTop: '40px' }}>
                <h2 className={styles.sectionTitle}>Unit Conversions</h2>
                <table className={styles.transformTable}>
                  <thead>
                    <tr>
                      <th>Original System</th>
                      <th>Target Metric</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.dimensions.map((dim, index) => (
                      <tr key={index}>
                        <td>{dim.original_value} {dim.original_unit}</td>
                        <td>{dim.normalized_value} {dim.normalized_unit}</td>
                        <td>
                          {dim.ambiguous ? (
                            <span className={styles.confidenceMed}>Ambiguous Context</span>
                          ) : (
                            <span className={styles.confidenceHigh}>Standard Conversion</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            
            {result.expanded_abbreviations.length === 0 && result.dimensions.length === 0 && (
              <div className={styles.emptyState}>
                <p>No specific abbreviations expanded or dimensions converted.</p>
              </div>
            )}
          </>
        ) : (
          <div className={styles.emptyState}>
            <p>Enter a material description above to test the normalization pipeline.</p>
            <div className={styles.examplePrompts}>
              <button onClick={() => setInputText('CS PIPE 10 IN SCH40')} type="button" className={styles.exampleTag}>
                CS PIPE 10 IN SCH40
              </button>
              <button onClick={() => setInputText('SS BOLT M16 X 50MM')} type="button" className={styles.exampleTag}>
                SS BOLT M16 X 50MM
              </button>
              <button onClick={() => setInputText('BRASS FITTING 2 LBS')} type="button" className={styles.exampleTag}>
                BRASS FITTING 2 LBS
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Normalization;
