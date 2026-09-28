import { useState, useCallback } from 'react';
import ReactFlow, { 
  MiniMap, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Filter } from 'lucide-react';
import styles from './MaterialGraph.module.css';

const initialNodes = [
  { id: '1', position: { x: 400, y: 100 }, data: { label: 'CNMC-000001 (National Master)' }, style: { backgroundColor: 'var(--color-primary)', color: 'white', fontWeight: 600, border: 'none', padding: '10px 20px', borderRadius: '8px' } },
  
  { id: '2', position: { x: 200, y: 250 }, data: { label: 'IOCL: 101' }, style: { backgroundColor: '#f8fafc', border: '2px solid #cbd5e1', borderRadius: '4px' } },
  { id: '3', position: { x: 400, y: 250 }, data: { label: 'NTPC: P-782' }, style: { backgroundColor: '#f8fafc', border: '2px solid #cbd5e1', borderRadius: '4px' } },
  { id: '4', position: { x: 600, y: 250 }, data: { label: 'BHEL: PIPE-55' }, style: { backgroundColor: '#f8fafc', border: '2px solid #cbd5e1', borderRadius: '4px' } },

  { id: 'a1', position: { x: 100, y: 400 }, data: { label: 'Material: CS' }, style: { backgroundColor: '#ecfeff', border: '1px solid #06b6d4', borderRadius: '20px' } },
  { id: 'a2', position: { x: 300, y: 400 }, data: { label: 'Form: Pipe' }, style: { backgroundColor: '#ecfeff', border: '1px solid #06b6d4', borderRadius: '20px' } },
  { id: 'a3', position: { x: 500, y: 400 }, data: { label: 'Size: 10"' }, style: { backgroundColor: '#ecfeff', border: '1px solid #06b6d4', borderRadius: '20px' } },
  { id: 'a4', position: { x: 700, y: 400 }, data: { label: 'Sch: 40' }, style: { backgroundColor: '#ecfeff', border: '1px solid #06b6d4', borderRadius: '20px' } },
];

const initialEdges = [
  { id: 'e1-2', source: '2', target: '1', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e1-3', source: '3', target: '1', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e1-4', source: '4', target: '1', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },

  { id: 'ea1-2', source: 'a1', target: '2', style: { stroke: '#94a3b8' } },
  { id: 'ea2-2', source: 'a2', target: '2', style: { stroke: '#94a3b8' } },
  { id: 'ea3-2', source: 'a3', target: '2', style: { stroke: '#94a3b8' } },
  { id: 'ea4-2', source: 'a4', target: '2', style: { stroke: '#94a3b8' } },

  { id: 'ea1-3', source: 'a1', target: '3', style: { stroke: '#94a3b8' } },
  { id: 'ea2-3', source: 'a2', target: '3', style: { stroke: '#94a3b8' } },
  { id: 'ea3-3', source: 'a3', target: '3', style: { stroke: '#94a3b8' } },
  { id: 'ea4-3', source: 'a4', target: '3', style: { stroke: '#94a3b8' } },

  { id: 'ea1-4', source: 'a1', target: '4', style: { stroke: '#94a3b8' } },
  { id: 'ea2-4', source: 'a2', target: '4', style: { stroke: '#94a3b8' } },
  { id: 'ea3-4', source: 'a3', target: '4', style: { stroke: '#94a3b8' } },
  { id: 'ea4-4', source: 'a4', target: '4', style: { stroke: '#94a3b8' } },
];

const MaterialGraph = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [showAttributes, setShowAttributes] = useState(true);

  const toggleAttributes = useCallback(() => {
    setShowAttributes((prev) => !prev);
    if (showAttributes) {
      setNodes((nds) => nds.filter((node) => !node.id.startsWith('a')));
      setEdges((eds) => eds.filter((edge) => !edge.id.startsWith('ea')));
    } else {
      setNodes(initialNodes);
      setEdges(initialEdges);
    }
  }, [showAttributes, setNodes, setEdges]);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>Material Knowledge Graph</h1>
          <p className={styles.subtitle}>Explore relationships between National Masters, CPSE codes, and material attributes.</p>
        </div>
      </div>

      <div className={styles.graphContainer}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          attributionPosition="bottom-right"
        >
          <Controls />
          <MiniMap />
          <Background color="#e2e8f0" gap={16} />
        </ReactFlow>

        <div className={styles.sidebar}>
          <h3 className={styles.sidebarTitle}><Filter size={18} /> Graph Controls</h3>
          
          <div className={styles.filterGroup}>
            <span className={styles.filterLabel}>Node Types</span>
            <label className={styles.checkbox}>
              <input type="checkbox" checked={true} readOnly /> National Masters (CNMC)
            </label>
            <label className={styles.checkbox}>
              <input type="checkbox" checked={true} readOnly /> CPSE Material Codes
            </label>
            <label className={styles.checkbox}>
              <input type="checkbox" checked={showAttributes} onChange={toggleAttributes} /> Technical Attributes
            </label>
          </div>

          <div className={styles.legend}>
            <div className={styles.legendItem}>
              <div className={styles.colorDot} style={{ backgroundColor: 'var(--color-primary)' }}></div>
              <span>National Master Node</span>
            </div>
            <div className={styles.legendItem}>
              <div className={styles.colorDot} style={{ backgroundColor: '#cbd5e1' }}></div>
              <span>CPSE Material Node</span>
            </div>
            <div className={styles.legendItem}>
              <div className={styles.colorDot} style={{ backgroundColor: '#06b6d4' }}></div>
              <span>Attribute Node</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MaterialGraph;
