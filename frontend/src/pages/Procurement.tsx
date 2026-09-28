import { TrendingDown, TrendingUp, AlertTriangle, CheckCircle, PackageSearch, Activity } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import styles from './Procurement.module.css';

const savingsData = [
  { month: 'Jan', savings: 4000 },
  { month: 'Feb', savings: 7000 },
  { month: 'Mar', savings: 12000 },
  { month: 'Apr', savings: 27800 },
  { month: 'May', savings: 48900 },
  { month: 'Jun', savings: 63900 },
];

const vendorData = [
  { name: 'Supplier A', volume: 4000 },
  { name: 'Supplier B', volume: 3000 },
  { name: 'Supplier C', volume: 2000 },
  { name: 'Supplier D', volume: 2780 },
  { name: 'Supplier E', volume: 1890 },
];

const Procurement = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>Procurement Intelligence</h1>
          <p className={styles.subtitle}>Analyze savings, vendor performance, and cross-CPSE procurement opportunities.</p>
        </div>
      </div>

      <div className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span className={styles.kpiTitle}>Total Savings Identified</span>
            <TrendingDown size={20} className={styles.trendPositive} />
          </div>
          <div className={styles.kpiValue}>₹14.2 Cr</div>
          <div className={styles.trend + ' ' + styles.trendPositive}>
            <TrendingUp size={14} /> +12% from last quarter
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span className={styles.kpiTitle}>Joint Procurement Opps</span>
            <PackageSearch size={20} className={styles.trendPositive} />
          </div>
          <div className={styles.kpiValue}>243 SKUs</div>
          <div className={styles.trend + ' ' + styles.trendPositive}>
            <TrendingUp size={14} /> High feasibility
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span className={styles.kpiTitle}>Vendor Risk Incidents</span>
            <AlertTriangle size={20} className={styles.trendNegative} />
          </div>
          <div className={styles.kpiValue}>12</div>
          <div className={styles.trend + ' ' + styles.trendNegative}>
            <TrendingDown size={14} /> Needs attention
          </div>
        </div>
        
        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span className={styles.kpiTitle}>Active Tenders Monitored</span>
            <Activity size={20} className={styles.trendPositive} />
          </div>
          <div className={styles.kpiValue}>45</div>
          <div className={styles.trend + ' ' + styles.trendPositive}>
            <CheckCircle size={14} /> On track
          </div>
        </div>
      </div>

      <div className={styles.chartsGrid}>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Cumulative Cost Savings (Through Standardization)</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={savingsData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} tickFormatter={(val) => `${val / 1000}k`} />
                <Tooltip />
                <Area type="monotone" dataKey="savings" stroke="#0ea5e9" fill="#e0f2fe" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Top Vendors by Volume</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={vendorData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} width={80} />
                <Tooltip />
                <Bar dataKey="volume" fill="#0f172a" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className={styles.chartCard}>
        <h3 className={styles.chartTitle}>Joint Procurement Opportunities</h3>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>CNMC ID</th>
              <th>Material Description</th>
              <th>Interested CPSEs</th>
              <th>Est. Volume</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong style={{ color: 'var(--color-primary)' }}>CNMC-000001</strong></td>
              <td>Carbon Steel Seamless Pipe 10" Sch 40</td>
              <td>IOCL, NTPC, BHEL</td>
              <td>12,500 m</td>
              <td><span className={styles.badge + ' ' + styles.badgeOpt}>Highly Feasible</span></td>
            </tr>
            <tr>
              <td><strong style={{ color: 'var(--color-primary)' }}>CNMC-000492</strong></td>
              <td>Gate Valve 6" Class 150 Flanged</td>
              <td>ONGC, GAIL</td>
              <td>450 units</td>
              <td><span className={styles.badge + ' ' + styles.badgeOpt}>Feasible</span></td>
            </tr>
            <tr>
              <td><strong style={{ color: 'var(--color-primary)' }}>CNMC-001204</strong></td>
              <td>Transformer Oil Class A</td>
              <td>NTPC, PowerGrid</td>
              <td>50,000 L</td>
              <td><span className={styles.badge + ' ' + styles.badgeWarn}>Review Required</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Procurement;
