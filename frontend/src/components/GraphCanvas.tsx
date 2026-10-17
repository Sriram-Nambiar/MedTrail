import React, { useRef, useEffect, useState, useCallback } from 'react';
import type { GraphNode, GraphLink } from '../types/graph';
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

interface GraphCanvasProps {
  nodes: GraphNode[];
  links: GraphLink[];
  selectedNode: GraphNode | null;
  onSelectNode: (node: GraphNode | null) => void;
}

interface SimNode extends GraphNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({
  nodes,
  links,
  selectedNode,
  onSelectNode,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Transform (pan & zoom)
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 0.95 });
  const [hoveredNode, setHoveredNode] = useState<SimNode | null>(null);

  // Simulation nodes & map
  const simNodesRef = useRef<SimNode[]>([]);
  const isDraggingRef = useRef(false);
  const draggedNodeRef = useRef<SimNode | null>(null);
  const lastMousePosRef = useRef({ x: 0, y: 0 });
  const animFrameRef = useRef<number | null>(null);

  // Particle packet animation along links (papers flowing)
  const particleOffsetRef = useRef<number>(0);

  // Initialize simulation positions when nodes change
  useEffect(() => {
    const width = containerRef.current?.clientWidth || 800;
    const height = containerRef.current?.clientHeight || 600;

    const prevMap = new Map(simNodesRef.current.map((n) => [n.id, n]));

    simNodesRef.current = nodes.map((node, i) => {
      const prev = prevMap.get(node.id);
      if (prev) {
        return { ...node, x: prev.x, y: prev.y, vx: 0, vy: 0 };
      }
      const angle = (i / Math.max(nodes.length, 1)) * 2 * Math.PI;
      const radius = Math.min(width, height) * 0.38 + (Math.random() - 0.5) * 60;
      return {
        ...node,
        x: width / 2 + Math.cos(angle) * radius,
        y: height / 2 + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
      };
    });

    setTransform({ x: 0, y: 0, k: 0.95 });
  }, [nodes]);

  // Physics simulation step
  const tickPhysics = useCallback(() => {
    const simNodes = simNodesRef.current;
    if (simNodes.length === 0) return;

    const width = containerRef.current?.clientWidth || 800;
    const height = containerRef.current?.clientHeight || 600;
    const centerX = width / 2;
    const centerY = height / 2;

    const nodeMap = new Map(simNodes.map((n) => [n.id, n]));

    // 1. Repulsion between all node cards
    const kRepel = 2200;
    for (let i = 0; i < simNodes.length; i++) {
      const n1 = simNodes[i];
      for (let j = i + 1; j < simNodes.length; j++) {
        const n2 = simNodes[j];
        const dx = n2.x - n1.x;
        const dy = n2.y - n1.y;
        const distSq = dx * dx + dy * dy + 150;
        const dist = Math.sqrt(distSq);
        const force = kRepel / distSq;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        n1.vx -= fx;
        n1.vy -= fy;
        n2.vx += fx;
        n2.vy += fy;
      }
    }

    // 2. Attraction along links (Spring force)
    const idealDist = 130;
    const kSpring = 0.035;
    for (const link of links) {
      const s = nodeMap.get(link.source);
      const t = nodeMap.get(link.target);
      if (s && t) {
        const dx = t.x - s.x;
        const dy = t.y - s.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = (dist - idealDist) * kSpring;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        s.vx += fx;
        s.vy += fy;
        t.vx -= fx;
        t.vy -= fy;
      }
    }

    // 3. Center gravity pull & damping
    const kCenter = 0.012;
    for (const n of simNodes) {
      n.vx += (centerX - n.x) * kCenter;
      n.vy += (centerY - n.y) * kCenter;

      n.vx *= 0.85;
      n.vy *= 0.85;

      if (n !== draggedNodeRef.current) {
        n.x += n.vx;
        n.y += n.vy;
      }
    }
  }, [links]);

  // Render Canvas loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let running = true;

    // Helper: Draw research paper document card
    const drawPaperCard = (
      n: SimNode,
      isSelected: boolean,
      isHovered: boolean,
      isDimmed: boolean
    ) => {
      const cardW = 84;
      const cardH = 50;
      const x = n.x - cardW / 2;
      const y = n.y - cardH / 2;
      const radius = 6;
      const foldSize = 9;

      ctx.save();
      if (isDimmed) {
        ctx.globalAlpha = 0.22;
      }

      // Drop Shadow
      ctx.shadowColor = isSelected ? 'rgba(37, 99, 235, 0.4)' : 'rgba(15, 23, 42, 0.08)';
      ctx.shadowBlur = isSelected ? 12 : 6;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = isSelected ? 3 : 2;

      // Card Base Path (with folded top-right corner)
      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + cardW - foldSize, y);
      ctx.lineTo(x + cardW, y + foldSize);
      ctx.lineTo(x + cardW, y + cardH - radius);
      ctx.arcTo(x + cardW, y + cardH, x + cardW - radius, y + cardH, radius);
      ctx.lineTo(x + radius, y + cardH);
      ctx.arcTo(x, y + cardH, x, y + cardH - radius, radius);
      ctx.lineTo(x, y + radius);
      ctx.arcTo(x, y, x + radius, y, radius);
      ctx.closePath();

      // Card Background
      ctx.fillStyle = isSelected ? '#F8FAFC' : '#FFFFFF';
      ctx.fill();

      // Border outline
      ctx.shadowColor = 'transparent';
      ctx.lineWidth = isSelected ? 2 : 1;
      ctx.strokeStyle = isSelected ? '#2563EB' : isHovered ? '#94A3B8' : '#CBD5E1';
      ctx.stroke();

      // Folded Corner Dog-Ear
      ctx.beginPath();
      ctx.moveTo(x + cardW - foldSize, y);
      ctx.lineTo(x + cardW - foldSize, y + foldSize);
      ctx.lineTo(x + cardW, y + foldSize);
      ctx.closePath();
      ctx.fillStyle = '#E2E8F0';
      ctx.fill();
      ctx.strokeStyle = '#CBD5E1';
      ctx.lineWidth = 0.8;
      ctx.stroke();

      // Top Colored Header Stripe
      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + cardW - foldSize, y);
      ctx.lineTo(x + cardW - foldSize, y + 4);
      ctx.lineTo(x, y + 4);
      ctx.lineTo(x, y + radius);
      ctx.arcTo(x, y, x + radius, y, radius);
      ctx.closePath();
      ctx.fillStyle = n.color;
      ctx.fill();

      // Type Badge (small text at top)
      ctx.font = '8px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      ctx.fillStyle = '#64748B';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'top';
      ctx.fillText(n.type.toUpperCase(), x + 6, y + 7);

      // Node Label (Title of Paper / Drug / Gene)
      ctx.font = `${isSelected ? 'bold 10px' : '500 10px'} -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
      ctx.fillStyle = isSelected ? '#1E3A8A' : '#0F172A';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';

      const maxChars = 13;
      const displayLabel = n.label.length > maxChars ? n.label.slice(0, maxChars - 1) + '…' : n.label;
      ctx.fillText(displayLabel, x + 6, y + 23);

      // Micro Document Text Lines (Simulating abstract lines on paper)
      ctx.fillStyle = '#E2E8F0';
      ctx.fillRect(x + 6, y + 33, cardW - 20, 2);
      ctx.fillRect(x + 6, y + 38, cardW - 32, 2);

      // Tiny ID indicator on bottom right
      ctx.font = '7.5px monospace';
      ctx.fillStyle = '#94A3B8';
      ctx.textAlign = 'right';
      const idTag = n.properties?.pmid ? `PMID:${n.properties.pmid}` : n.properties?.nct_id || '';
      if (idTag) {
        ctx.fillText(idTag.slice(0, 10), x + cardW - 6, y + cardH - 6);
      }

      ctx.restore();
    };

    const render = () => {
      if (!running) return;

      tickPhysics();
      particleOffsetRef.current = (particleOffsetRef.current + 0.008) % 1;

      const width = canvas.width;
      const height = canvas.height;

      ctx.clearRect(0, 0, width, height);
      ctx.save();

      // Pan & Zoom
      ctx.translate(transform.x, transform.y);
      ctx.scale(transform.k, transform.k);

      const simNodes = simNodesRef.current;
      const nodeMap = new Map(simNodes.map((n) => [n.id, n]));

      // Determine connected nodes if selected
      const connectedNodeIds = new Set<string>();
      if (selectedNode) {
        connectedNodeIds.add(selectedNode.id);
        for (const l of links) {
          if (l.source === selectedNode.id) connectedNodeIds.add(l.target);
          if (l.target === selectedNode.id) connectedNodeIds.add(l.source);
        }
      }

      // Draw Connection Links
      for (const link of links) {
        const s = nodeMap.get(link.source);
        const t = nodeMap.get(link.target);
        if (!s || !t) continue;

        const isHighlighted =
          selectedNode &&
          (link.source === selectedNode.id || link.target === selectedNode.id);

        const isDimmed = selectedNode && !isHighlighted;

        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.strokeStyle = isHighlighted
          ? '#2563EB'
          : isDimmed
          ? 'rgba(226, 232, 240, 0.35)'
          : 'rgba(203, 213, 225, 0.7)';
        ctx.lineWidth = isHighlighted ? 2.5 : 1.2;
        ctx.stroke();

        // Animated Mini "Flying Research Papers" traveling along the links
        if (!isDimmed) {
          const tOffset = (particleOffsetRef.current + (link.source.charCodeAt(0) % 10) * 0.1) % 1;
          const px = s.x + (t.x - s.x) * tOffset;
          const py = s.y + (t.y - s.y) * tOffset;

          // Mini flying paper rectangle
          ctx.save();
          ctx.translate(px, py);
          const angle = Math.atan2(t.y - s.y, t.x - s.x);
          ctx.rotate(angle);

          ctx.fillStyle = isHighlighted ? '#3B82F6' : '#94A3B8';
          ctx.fillRect(-5, -3.5, 10, 7);
          ctx.fillStyle = '#FFFFFF';
          ctx.fillRect(-3, -2, 6, 4);
          ctx.restore();
        }

        // Label on link if highlighted
        if (isHighlighted) {
          const midX = (s.x + t.x) / 2;
          const midY = (s.y + t.y) / 2;
          ctx.font = '10px sans-serif';
          ctx.fillStyle = '#1E293B';
          ctx.fillText(link.label, midX, midY - 4);
        }
      }

      // Draw Research Paper Cards for all nodes
      for (const n of simNodes) {
        const isSelected = selectedNode?.id === n.id;
        const isConnected = connectedNodeIds.has(n.id);
        const isHovered = hoveredNode?.id === n.id;
        const isDimmed = Boolean(selectedNode && !isSelected && !isConnected);

        drawPaperCard(n, isSelected, isHovered, isDimmed);
      }

      ctx.restore();
      animFrameRef.current = requestAnimationFrame(render);
    };

    animFrameRef.current = requestAnimationFrame(render);

    return () => {
      running = false;
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [links, selectedNode, hoveredNode, transform, tickPhysics]);

  // Handle Resize
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current && canvasRef.current) {
        canvasRef.current.width = containerRef.current.clientWidth;
        canvasRef.current.height = containerRef.current.clientHeight;
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Coordinate helper: Screen coords to Canvas World coords
  const screenToWorld = (screenX: number, screenY: number) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return { x: 0, y: 0 };
    const x = (screenX - rect.left - transform.x) / transform.k;
    const y = (screenY - rect.top - transform.y) / transform.k;
    return { x, y };
  };

  // Find node card under mouse (bounding box 84 x 50)
  const getNodeAt = (screenX: number, screenY: number): SimNode | null => {
    const { x, y } = screenToWorld(screenX, screenY);
    const halfW = 42;
    const halfH = 25;
    for (const node of simNodesRef.current) {
      if (
        x >= node.x - halfW &&
        x <= node.x + halfW &&
        y >= node.y - halfH &&
        y <= node.y + halfH
      ) {
        return node;
      }
    }
    return null;
  };

  // Mouse Handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    const node = getNodeAt(e.clientX, e.clientY);
    if (node) {
      draggedNodeRef.current = node;
      isDraggingRef.current = true;
    } else {
      isDraggingRef.current = true;
      draggedNodeRef.current = null;
    }
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    const node = getNodeAt(e.clientX, e.clientY);
    setHoveredNode(node);

    if (!isDraggingRef.current) return;

    const dx = e.clientX - lastMousePosRef.current.x;
    const dy = e.clientY - lastMousePosRef.current.y;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };

    if (draggedNodeRef.current) {
      draggedNodeRef.current.x += dx / transform.k;
      draggedNodeRef.current.y += dy / transform.k;
    } else {
      setTransform((prev) => ({
        ...prev,
        x: prev.x + dx,
        y: prev.y + dy,
      }));
    }
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    if (
      Math.abs(e.clientX - lastMousePosRef.current.x) < 4 &&
      Math.abs(e.clientY - lastMousePosRef.current.y) < 4
    ) {
      const clicked = getNodeAt(e.clientX, e.clientY);
      onSelectNode(clicked);
    }
    isDraggingRef.current = false;
    draggedNodeRef.current = null;
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
    const newK = Math.min(Math.max(transform.k * zoomFactor, 0.2), 3.5);

    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    setTransform((prev) => ({
      k: newK,
      x: mouseX - (mouseX - prev.x) * (newK / prev.k),
      y: mouseY - (mouseY - prev.y) * (newK / prev.k),
    }));
  };

  const handleZoom = (direction: 'in' | 'out' | 'reset') => {
    if (direction === 'reset') {
      setTransform({ x: 0, y: 0, k: 0.95 });
      return;
    }
    const factor = direction === 'in' ? 1.2 : 0.8;
    const newK = Math.min(Math.max(transform.k * factor, 0.2), 3.5);
    const width = containerRef.current?.clientWidth || 800;
    const height = containerRef.current?.clientHeight || 600;

    setTransform((prev) => ({
      k: newK,
      x: width / 2 - (width / 2 - prev.x) * (newK / prev.k),
      y: height / 2 - (height / 2 - prev.y) * (newK / prev.k),
    }));
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full min-h-[550px] bg-slate-50/60 rounded-xl overflow-hidden border border-slate-200 select-none"
    >
      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onWheel={handleWheel}
        className="w-full h-full cursor-grab active:cursor-grabbing block"
      />

      {/* Floating Zoom Controls */}
      <div className="absolute bottom-4 right-4 flex items-center bg-white/95 backdrop-blur-sm border border-slate-200 rounded-lg shadow-sm p-1 gap-1 z-10">
        <button
          onClick={() => handleZoom('in')}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded transition"
          title="Zoom In"
        >
          <ZoomIn size={16} />
        </button>
        <button
          onClick={() => handleZoom('out')}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded transition"
          title="Zoom Out"
        >
          <ZoomOut size={16} />
        </button>
        <button
          onClick={() => handleZoom('reset')}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded transition"
          title="Reset View"
        >
          <RotateCcw size={16} />
        </button>
      </div>

      {/* Document Legend */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm border border-slate-200 rounded-lg shadow-sm px-3 py-1.5 flex items-center gap-3 text-xs text-slate-600 z-10">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-3.5 border border-red-500 rounded-xs bg-red-50 inline-block" /> Disease
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-3.5 border border-purple-500 rounded-xs bg-purple-50 inline-block" /> Pathway
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-3.5 border border-cyan-500 rounded-xs bg-cyan-50 inline-block" /> Target
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-3.5 border border-emerald-500 rounded-xs bg-emerald-50 inline-block" /> Drug
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-3.5 border border-amber-500 rounded-xs bg-amber-50 inline-block" /> Trial
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-3.5 border border-teal-500 rounded-xs bg-teal-50 inline-block" /> Evidence
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-3.5 border border-indigo-500 rounded-xs bg-indigo-50 inline-block" /> Paper
        </span>
      </div>
    </div>
  );
};
