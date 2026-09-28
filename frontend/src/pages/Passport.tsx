import { Fingerprint, Search, ShieldCheck, Factory, Truck, CheckCircle2 } from 'lucide-react';
import styles from './Passport.module.css';

const Passport = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>Material Passport</h1>
          <p className={styles.subtitle}>Trace origin, quality certifications, and movement history of standardized materials.</p>
        </div>
        <div className={styles.searchBar}>
          <input type="text" placeholder="Enter CNMC, CPSE Code, or Batch No..." className={styles.searchInput} />
          <button className={styles.searchBtn}><Search size={18} /></button>
        </div>
      </div>

      <div className={styles.passportCard}>
        <div className={styles.passportHeader}>
          <div>
            <div className={styles.passportId}>CNMC-000001</div>
            <div className={styles.passportDesc}>Carbon Steel Seamless Pipe 10" Sch 40</div>
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
                <div className={styles.detailItem}>
                  <span className={styles.detailLabel}>Standard</span>
                  <span className={styles.detailValue}>ASME B36.10</span>
                </div>
                <div className={styles.detailItem}>
                  <span className={styles.detailLabel}>Material Grade</span>
                  <span className={styles.detailValue}>ASTM A106 Gr B</span>
                </div>
                <div className={styles.detailItem}>
                  <span className={styles.detailLabel}>Dimensions</span>
                  <span className={styles.detailValue}>10" (273.1mm OD) x Sch 40 (9.27mm Wall)</span>
                </div>
                <div className={styles.detailItem}>
                  <span className={styles.detailLabel}>End Prep</span>
                  <span className={styles.detailValue}>Beveled Ends (BE)</span>
                </div>
              </div>
            </div>

            <div className={styles.section}>
              <h3 className={styles.sectionTitle}><ShieldCheck size={18} /> Certifications & Compliance</h3>
              <div>
                <div className={styles.certBadge}><CheckCircle2 size={16} /> ISO 9001:2015 Verified</div>
                <div className={styles.certBadge}><CheckCircle2 size={16} /> IBR Certified</div>
              </div>
            </div>
          </div>

          <div>
            <div className={styles.section}>
              <h3 className={styles.sectionTitle}><Truck size={18} /> Provenance Track</h3>
              <div className={styles.timeline}>
                <div className={styles.timelineItem}>
                  <div className={styles.timelineIcon}><Factory size={12} /></div>
                  <div className={styles.timelineContent}>
                    <div className={styles.timelineTitle}>Manufactured by Jindal SAW</div>
                    <div className={styles.timelineDate}>Oct 12, 2026 - Batch JS-8992</div>
                  </div>
                </div>
                <div className={styles.timelineItem}>
                  <div className={styles.timelineIcon}><ShieldCheck size={12} /></div>
                  <div className={styles.timelineContent}>
                    <div className={styles.timelineTitle}>Quality Passed (TPI)</div>
                    <div className={styles.timelineDate}>Oct 15, 2026 - Certificate #QA-455</div>
                  </div>
                </div>
                <div className={styles.timelineItem}>
                  <div className={styles.timelineIcon}><Truck size={12} /></div>
                  <div className={styles.timelineContent}>
                    <div className={styles.timelineTitle}>Received at IOCL Panipat</div>
                    <div className={styles.timelineDate}>Oct 20, 2026 - GRN #100234</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Passport;
