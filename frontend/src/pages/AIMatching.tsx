import { useState, useEffect } from 'react';
import { BrainCircuit, Check, CheckCircle2, AlertTriangle, ShieldAlert } from 'lucide-react';
import styles from './AIMatching.module.css';
import { matchingService } from '../services/matching';
import type { MatchResponse } from '../types/api';

const AIMatching = () => {
  const [data, setData] = useState<MatchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFirstMatch = async () => {
      try {
        setLoading(true);
        const res = await matchingService.getMatches({ page: 1, page_size: 1 });
        if (res.items && res.items.length > 0) {
          setData(res.items[0]);
        } else {
          setData(null);
        }
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch match data');
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchFirstMatch();
  }, []);

  if (loading) {
    return <div className={styles.container}><div style={{ padding: '24px' }}>Loading matching analysis...</div></div>;
  }

  if (error) {
    return <div className={styles.container}><div style={{ padding: '24px', color: 'var(--color-danger)' }}>Error: {error}</div></div>;
  }

  if (!data) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.titleGroup}>
            <h1 className={styles.title}>AI Material Matching</h1>
            <p className={styles.subtitle}>Comparing CPSE records using Fuzzy Similarity, Semantic Embeddings, and Technical Rules.</p>
          </div>
        </div>
        <div style={{ padding: '24px', backgroundColor: 'white', borderRadius: '8px', border: '1px solid var(--color-border)', marginTop: '24px' }}>
          No matching results available in the database.
        </div>
      </div>
    );
  }

  const { source_material, target_material, scores, explanation, technical_conflicts } = data;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>AI Material Matching</h1>
          <p className={styles.subtitle}>Comparing CPSE records using Fuzzy Similarity, Semantic Embeddings, and Technical Rules.</p>
        </div>
        {data.classification === 'REVIEW_REQUIRED' ? (
           <div className={styles.badge + ' ' + styles.badgeConflict} style={{ backgroundColor: 'var(--color-warning)', color: 'white' }}>
             <AlertTriangle size={16} /> REVIEW REQUIRED
           </div>
        ) : (
          <div className={styles.badge + ' ' + styles.badgeMatch}>
            <CheckCircle2 size={16} /> {data.classification.replace(/_/g, ' ')}
          </div>
        )}
      </div>

      <div className={styles.matchContainer}>
        {/* Left Record */}
        <div className={styles.recordCard}>
          <div className={styles.recordHeader}>
            <span className={styles.cpseName}>{source_material.cpse}</span>
            <span className={styles.materialCode}>{source_material.code}</span>
          </div>
          <div className={styles.recordDesc}>
            {source_material.description}
          </div>
          <div className={styles.pipelineFlow}>
            Extracted DNA: {source_material.normalized_description || 'N/A'}
          </div>
        </div>

        {/* AI Analysis Center */}
        <div className={styles.analysisCard}>
          <div className={styles.analysisTitle}>AI Confidence</div>
          <div className={styles.scoreCircle}>
            <span className={styles.scoreValue}>{Math.round((explanation.confidence || scores.final) * 100)}%</span>
            <span className={styles.scoreLabel}>CONFIDENCE</span>
          </div>
          
          <div className={styles.scoreMetrics}>
            <div className={styles.metricRow}>
              <span>Semantic Similarity</span>
              <span className={styles.metricValue}>{Math.round(scores.semantic * 100)}%</span>
            </div>
            <div className={styles.metricRow}>
              <span>Attribute Match</span>
              <span className={styles.metricValue}>{Math.round(scores.attribute * 100)}%</span>
            </div>
            <div className={styles.metricRow}>
              <span>Tech Compatibility</span>
              <span className={styles.metricValue}>{Math.round(scores.technical * 100)}%</span>
            </div>
          </div>
        </div>

        {/* Right Record */}
        <div className={styles.recordCard}>
          <div className={styles.recordHeader}>
            <span className={styles.cpseName}>{target_material.cpse}</span>
            <span className={styles.materialCode}>{target_material.code}</span>
          </div>
          <div className={styles.recordDesc}>
            {target_material.description}
          </div>
          <div className={styles.pipelineFlow}>
            Extracted DNA: {target_material.normalized_description || 'N/A'}
          </div>
        </div>
      </div>

      {/* Explainable AI Section */}
      <div className={styles.explainableSection}>
        <div className={styles.explainCard}>
          <h3 className={styles.explainTitle}>
            <CheckCircle2 size={20} className={styles.reasonIcon + ' ' + styles.success} /> 
            Why This Match?
          </h3>
          <div className={styles.reasonList}>
            {explanation.why_matched.length > 0 ? (
              explanation.why_matched.map((reason, idx) => (
                <div key={idx} className={styles.reasonItem}>
                  <Check size={16} className={styles.reasonIcon + ' ' + styles.success} />
                  <span>{reason}</span>
                </div>
              ))
            ) : (
              <div className={styles.reasonItem}>
                <span>No specific reasons provided.</span>
              </div>
            )}
            {explanation.what_matched.map((reason, idx) => (
              <div key={idx} className={styles.reasonItem}>
                <Check size={16} className={styles.reasonIcon + ' ' + styles.success} />
                <span>Same {reason}</span>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.explainCard}>
          <h3 className={styles.explainTitle}>
            <AlertTriangle size={20} className={styles.reasonIcon + ' ' + styles.warning} /> 
            Technical Differences
          </h3>
          <div className={styles.reasonList}>
            {explanation.what_differed.length > 0 ? (
              explanation.what_differed.map((diff, idx) => (
                <div key={idx} className={styles.reasonItem}>
                  <AlertTriangle size={16} className={styles.reasonIcon + ' ' + styles.warning} />
                  <span>{diff} differed</span>
                </div>
              ))
            ) : (
              <div className={styles.reasonItem}>
                <span>No significant differences detected.</span>
              </div>
            )}
          </div>
        </div>

        {/* Explainable Reasoning Summary */}
        <div className={styles.summaryBox}>
          <BrainCircuit size={24} className={styles.summaryIcon} />
          <div className={styles.summaryContent}>
            <h3>AI Reasoning Summary</h3>
            <p>
              {explanation.recommendation || "Pending recommendation"}
            </p>
          </div>
        </div>
      </div>

      {/* Critical Differences */}
      {technical_conflicts && technical_conflicts.length > 0 && (
        <>
          <div className={styles.header} style={{ marginTop: '40px' }}>
            <div className={styles.titleGroup}>
              <h2 className={styles.title} style={{ fontSize: '1.25rem' }}>Conflict Detection</h2>
              <p className={styles.subtitle}>Demonstrating semantic similarities that hide critical technical conflicts.</p>
            </div>
            <div className={styles.badge + ' ' + styles.badgeConflict}>
              <ShieldAlert size={16} /> DO NOT AUTO-MERGE
            </div>
          </div>

          {technical_conflicts.map((conflict, idx) => (
            <div key={idx} className={styles.summaryBox} style={{ backgroundColor: 'var(--color-danger-bg)', borderColor: 'rgba(225, 29, 72, 0.2)', marginBottom: '16px' }}>
              <AlertTriangle size={24} style={{ color: 'var(--color-danger)' }} />
              <div className={styles.summaryContent}>
                <h3 style={{ color: 'var(--color-danger)' }}>{conflict.severity} TECHNICAL DIFFERENCE: {conflict.attribute.toUpperCase()}</h3>
                <p>
                  <strong>{source_material.cpse} ({conflict.source_value || 'None'})</strong> vs <strong>{target_material.cpse} ({conflict.target_value || 'None'})</strong><br />
                  {conflict.reason}
                </p>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
};

export default AIMatching;
