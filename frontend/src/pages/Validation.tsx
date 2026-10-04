import { useState, useEffect } from 'react';
import { Check, X, Edit3, ShieldCheck, AlertCircle, Loader } from 'lucide-react';
import styles from './Validation.module.css';
import { validationService } from '../services/validation';
import type { ReviewResponse } from '../types/api';

const Validation = () => {
  const [reviews, setReviews] = useState<ReviewResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [comments, setComments] = useState<Record<number, string>>({});

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const data = await validationService.getReviews('PENDING');
      setReviews(data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch reviews', err);
      setError('Failed to load pending reviews. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      setActionLoading(id);
      await validationService.approveReview(id, comments[id]);
      // Remove from list
      setReviews(reviews.filter(r => r.id !== id));
    } catch (err) {
      console.error('Failed to approve review', err);
      alert('Failed to approve review. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (id: number) => {
    try {
      setActionLoading(id);
      await validationService.rejectReview(id, comments[id]);
      // Remove from list
      setReviews(reviews.filter(r => r.id !== id));
    } catch (err) {
      console.error('Failed to reject review', err);
      alert('Failed to reject review. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCommentChange = (id: number, text: string) => {
    setComments(prev => ({ ...prev, [id]: text }));
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>AI Review Queue</h1>
          <p className={styles.subtitle}>Human expert validation for AI-generated material clusters.</p>
        </div>
      </div>

      {loading ? (
        <div className={styles.messageBox} style={{ justifyContent: 'center' }}>
          <Loader className="animate-spin" size={20} />
          <span>Loading validation queue...</span>
        </div>
      ) : error ? (
        <div className={styles.messageBox} style={{ color: 'red' }}>
          <AlertCircle size={20} />
          {error}
        </div>
      ) : reviews.length === 0 ? (
        <div className={styles.messageBox}>
          <ShieldCheck size={20} />
          No pending reviews available in the database.
        </div>
      ) : (
        reviews.map((review) => (
          <div key={review.id} className={styles.clusterCard} style={{ marginBottom: '24px' }}>
            <div className={styles.clusterHeader}>
              <div className={styles.clusterInfo}>
                <span className={styles.clusterId}>Match: {review.match_id}</span>
                <span className={styles.badge + ' ' + styles.badgeWarning}>Priority: {review.priority}</span>
                <span className={styles.badge + ' ' + styles.badgeSuccess}>Confidence: {review.ai_confidence ? (review.ai_confidence * 100).toFixed(0) + '%' : 'N/A'}</span>
              </div>
              <div className={styles.actionButtons}>
                <button 
                  className={styles.btn + ' ' + styles.btnReject} 
                  onClick={() => handleReject(review.id)}
                  disabled={actionLoading === review.id}
                >
                  <X size={16} /> Reject
                </button>
                <button className={styles.btn + ' ' + styles.btnEdit} disabled={actionLoading === review.id}>
                  <Edit3 size={16} /> Edit
                </button>
                <button 
                  className={styles.btn + ' ' + styles.btnApprove} 
                  onClick={() => handleApprove(review.id)}
                  disabled={actionLoading === review.id}
                >
                  <Check size={16} /> Approve
                </button>
              </div>
            </div>

            <div className={styles.candidatesGrid}>
              <div className={styles.candidateCard}>
                <div className={styles.candidateHeader}>
                  <span className={styles.cpseTag}>Source CPSE</span>
                  <span className={styles.materialCode}>{review.source_cpse_id || 'N/A'}</span>
                </div>
                <div className={styles.candidateDesc}>Source Material</div>
                <div className={styles.attributesList}>
                  <div className={styles.attribute}><span className={styles.attrLabel}>Material Code</span><span className={styles.attrValue}>{review.source_material_code || 'N/A'}</span></div>
                </div>
              </div>

              <div className={styles.candidateCard}>
                <div className={styles.candidateHeader}>
                  <span className={styles.cpseTag}>Target CPSE</span>
                  <span className={styles.materialCode}>{review.target_cpse_id || 'N/A'}</span>
                </div>
                <div className={styles.candidateDesc}>Target Material</div>
                <div className={styles.attributesList}>
                  <div className={styles.attribute}><span className={styles.attrLabel}>Material Code</span><span className={styles.attrValue}>{review.target_material_code || 'N/A'}</span></div>
                </div>
              </div>
            </div>

            <div className={styles.commentSection}>
              <div className={styles.commentHeader}>Reviewer Comment (Optional)</div>
              <textarea 
                className={styles.commentInput} 
                placeholder="e.g., Verified against technical specification."
                value={comments[review.id] || ''}
                onChange={(e) => handleCommentChange(review.id, e.target.value)}
                disabled={actionLoading === review.id}
              ></textarea>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-primary)', fontWeight: 500, fontSize: '0.875rem' }}>
                <AlertCircle size={16} /> AI recommends: {review.ai_recommendation || 'Unknown'} → Human decides
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default Validation;
