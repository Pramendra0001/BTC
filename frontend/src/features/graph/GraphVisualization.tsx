import { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { 
  ZoomIn, ZoomOut, Maximize2, RotateCcw, Download, 
  Layers, X
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

interface GraphVisualizationProps {
  elements: {
    nodes: Array<{ data: any }>;
    edges: Array<{ data: any }>;
  };
  centerEntityId?: string;
  onNodeSelect?: (nodeData: any) => void;
}

export function GraphVisualization({ elements, centerEntityId, onNodeSelect }: GraphVisualizationProps) {
  const { resolvedTheme } = useTheme();
  const isLight = resolvedTheme === 'light';
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [layoutName, setLayoutName] = useState<string>('concentric');
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Transform backend elements into Cytoscape format
    const cyElements: cytoscape.ElementDefinition[] = [];

    // Process nodes
    elements.nodes.forEach((n) => {
      const isCenter = n.data.is_center || n.data.id === centerEntityId || n.data.full_id === centerEntityId;
      const isAnomalous = (n.data.anomaly_score || 0) > 60;
      
      cyElements.push({
        group: 'nodes',
        data: {
          id: n.data.id,
          label: n.data.label || n.data.id,
          type: n.data.type,
          full_id: n.data.full_id || n.data.id,
          anomaly_score: n.data.anomaly_score,
          is_center: isCenter,
          is_anomalous: isAnomalous,
          ...n.data,
        }
      });
    });

    // Process edges
    elements.edges.forEach((e) => {
      cyElements.push({
        group: 'edges',
        data: {
          id: e.data.id,
          source: e.data.source,
          target: e.data.target,
          type: e.data.type,
          amount: e.data.amount,
          provenance: e.data.provenance,
          ...e.data,
        }
      });
    });

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: cyElements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': isLight ? '#cbd5e1' : '#334155',
            'label': 'data(label)',
            'color': isLight ? '#0f172a' : '#f8fafc',
            'font-size': '10px',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            'text-outline-color': isLight ? '#ffffff' : '#020617',
            'text-outline-width': 2,
            'width': 28,
            'height': 28,
            'border-width': 2,
            'border-color': isLight ? '#94a3b8' : '#475569',
          }
        },
        // WALLET Nodes
        {
          selector: 'node[type = "WALLET"]',
          style: {
            'background-color': '#2563eb',
            'border-color': '#60a5fa',
            'shape': 'ellipse',
          }
        },
        // TRANSACTION Nodes
        {
          selector: 'node[type = "TRANSACTION"]',
          style: {
            'background-color': '#9333ea',
            'border-color': '#c084fc',
            'shape': 'round-rectangle',
            'width': 24,
            'height': 24,
          }
        },
        // IP Nodes
        {
          selector: 'node[type = "IP"]',
          style: {
            'background-color': '#059669',
            'border-color': '#34d399',
            'shape': 'diamond',
            'width': 30,
            'height': 30,
          }
        },
        // ASN Nodes
        {
          selector: 'node[type = "ASN"]',
          style: {
            'background-color': '#d97706',
            'border-color': '#fbbf24',
            'shape': 'hexagon',
            'width': 32,
            'height': 32,
          }
        },
        // Anomalous Node Outline
        {
          selector: 'node[?is_anomalous]',
          style: {
            'border-color': '#ef4444',
            'border-width': 3,
            'border-style': 'solid',
            'shadow-blur': 12,
            'shadow-color': '#ef4444',
            'shadow-opacity': 0.8,
          }
        },
        // Center Selected Node
        {
          selector: 'node[?is_center]',
          style: {
            'border-color': '#38bdf8',
            'border-width': 4,
            'width': 36,
            'height': 36,
          }
        },
        // Edges
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': isLight ? '#94a3b8' : '#334155',
            'target-arrow-color': isLight ? '#64748b' : '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': 0.85,
          }
        },
        // Edge specific styles
        {
          selector: 'edge[type = "INPUT_OF"]',
          style: {
            'line-color': '#3b82f6',
            'target-arrow-color': '#3b82f6',
          }
        },
        {
          selector: 'edge[type = "OUTPUT_OF"]',
          style: {
            'line-color': '#8b5cf6',
            'target-arrow-color': '#8b5cf6',
          }
        },
        {
          selector: 'edge[type = "OBSERVED_FROM"]',
          style: {
            'line-color': '#10b981',
            'target-arrow-color': '#10b981',
            'line-style': 'dashed',
          }
        },
        {
          selector: 'edge[type = "COUNTERPARTY"]',
          style: {
            'line-color': '#eab308',
            'target-arrow-color': '#eab308',
            'line-style': 'dotted',
          }
        }
      ] as any,
      layout: {
        name: layoutName,
        animate: true,
        animationDuration: 500,
      } as any,
    });

    // Node selection event
    cy.on('tap', 'node', (evt) => {
      const nodeData = evt.target.data();
      setSelectedNode(nodeData);
      if (onNodeSelect) onNodeSelect(nodeData);
    });

    // Background click clears selection
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [elements, layoutName, centerEntityId, resolvedTheme, isLight, onNodeSelect]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit(undefined, 40);
  const handleReset = () => {
    cyRef.current?.reset();
    cyRef.current?.fit(undefined, 40);
  };

  const handleExportPNG = () => {
    if (!cyRef.current) return;
    const png64 = cyRef.current.png({ full: true, bg: '#020617' });
    const link = document.createElement('a');
    link.href = png64;
    link.download = `btc-shield-graph-${Date.now()}.png`;
    link.click();
  };

  return (
    <div className="relative w-full h-full min-h-[550px] bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
      {/* Graph Toolbar */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 bg-slate-900/90 backdrop-blur border border-slate-800 p-1.5 rounded-lg shadow-lg">
        {/* Layout Switcher */}
        <select
          value={layoutName}
          onChange={(e) => setLayoutName(e.target.value)}
          className="bg-slate-950 border border-slate-800 text-[11px] text-slate-200 rounded px-2 py-1 focus:outline-none"
        >
          <option value="concentric">Concentric Layout</option>
          <option value="circle">Circular Layout</option>
          <option value="breadthfirst">Breadth-First Hierarchy</option>
          <option value="grid">Grid Layout</option>
          <option value="random">Organic Layout</option>
        </select>

        <div className="h-4 w-[1px] bg-slate-800 mx-1" />

        {/* Zoom Controls */}
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          className="p-1 rounded hover:bg-slate-800 text-slate-300 hover:text-white"
        >
          <ZoomIn size={15} />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          className="p-1 rounded hover:bg-slate-800 text-slate-300 hover:text-white"
        >
          <ZoomOut size={15} />
        </button>
        <button
          onClick={handleFit}
          title="Fit to Screen"
          className="p-1 rounded hover:bg-slate-800 text-slate-300 hover:text-white"
        >
          <Maximize2 size={15} />
        </button>
        <button
          onClick={handleReset}
          title="Reset View"
          className="p-1 rounded hover:bg-slate-800 text-slate-300 hover:text-white"
        >
          <RotateCcw size={15} />
        </button>

        <div className="h-4 w-[1px] bg-slate-800 mx-1" />

        <button
          onClick={handleExportPNG}
          title="Export Graph Image"
          className="p-1 rounded hover:bg-slate-800 text-slate-300 hover:text-white flex items-center gap-1 text-[11px] px-2"
        >
          <Download size={13} /> Export PNG
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-slate-900/90 backdrop-blur border border-slate-800 p-2.5 rounded-lg shadow-lg text-[10px] space-y-1.5 font-mono">
        <div className="text-slate-400 font-bold mb-1">ENTITY TYPES</div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
          <span className="text-slate-300">Wallet</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded bg-purple-600" />
          <span className="text-slate-300">Transaction</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rotate-45 bg-emerald-600" />
          <span className="text-slate-300">IP Address</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-sm bg-amber-600" />
          <span className="text-slate-300">ASN</span>
        </div>
        <div className="flex items-center gap-2 pt-1 border-t border-slate-800">
          <span className="w-2.5 h-2.5 rounded-full border-2 border-rose-500 bg-transparent" />
          <span className="text-rose-400 font-bold">Anomalous (&gt;60)</span>
        </div>
      </div>

      {/* Main Cytoscape Container */}
      <div ref={containerRef} className="w-full h-full" />

      {/* Node Detail Drawer */}
      {selectedNode && (
        <div className="absolute top-4 right-4 z-20 w-80 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-2xl space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-blue-400 border border-slate-700">
              {selectedNode.type}
            </span>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-slate-400 hover:text-white"
            >
              <X size={14} />
            </button>
          </div>

          <div>
            <div className="text-xs text-slate-400">Identifier</div>
            <div className="text-xs font-mono text-white break-all select-all mt-0.5">
              {selectedNode.full_id || selectedNode.id}
            </div>
          </div>

          {selectedNode.anomaly_score !== undefined && (
            <div>
              <div className="text-xs text-slate-400">Anomaly Score</div>
              <div className="flex items-center gap-2 mt-1">
                <div className="flex-1 bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 to-rose-500" 
                    style={{ width: `${Math.min(selectedNode.anomaly_score, 100)}%` }}
                  />
                </div>
                <span className="font-mono text-xs font-bold text-rose-400">
                  {selectedNode.anomaly_score.toFixed(1)}
                </span>
              </div>
            </div>
          )}

          {selectedNode.country && (
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Country:</span>
              <span className="font-mono text-white">{selectedNode.country}</span>
            </div>
          )}

          {selectedNode.asn && (
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">ASN:</span>
              <span className="font-mono text-white">{selectedNode.asn}</span>
            </div>
          )}

          {selectedNode.tx_count !== undefined && (
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Transactions:</span>
              <span className="font-mono text-white">{selectedNode.tx_count}</span>
            </div>
          )}

          {/* Centrality info */}
          {selectedNode.centrality && (
            <div className="pt-2 border-t border-slate-800 text-[11px] space-y-1">
              <div className="text-slate-400 font-mono">GRAPH CENTRALITY</div>
              <div className="flex justify-between">
                <span className="text-slate-400">Degree:</span>
                <span className="font-mono text-white">{selectedNode.centrality.degree || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">PageRank:</span>
                <span className="font-mono text-white">{((selectedNode.centrality.pagerank || 0) * 100).toFixed(2)}%</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
