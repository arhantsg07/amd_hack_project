import { useRef, useEffect, useCallback } from 'react';
import ForceGraph2D, { ForceGraphMethods, NodeObject, LinkObject } from 'react-force-graph-2d';
import { motion } from 'framer-motion';
import type { WorkGraph, GraphNode, GraphEdge } from '../services/api';

interface GraphVisualizerProps {
    graph: WorkGraph | null;
    loading: boolean;
    onNodeClick?: (node: GraphNode) => void;
}

interface ForceNode extends NodeObject {
    id: string;
    type: string;
    label: string;
    color: string;
    size: number;
    activity_level: number;
    metadata: Record<string, unknown>;
}

interface ForceLink extends LinkObject {
    relationship: string;
    animated: boolean;
}

const NODE_COLORS: Record<string, string> = {
    person: '#00F0FF',
    task: '#FFB800',
    pr: '#FF6B6B',
    message: '#9D4EDD',
    channel: '#06D6A0',
};

export default function GraphVisualizer({ graph, loading, onNodeClick }: GraphVisualizerProps) {
    const graphRef = useRef<ForceGraphMethods>();
    const containerRef = useRef<HTMLDivElement>(null);

    // Convert graph data to force graph format
    const graphData = {
        nodes: graph?.nodes.map((n: GraphNode) => ({
            ...n,
            color: n.color || NODE_COLORS[n.type] || '#FFFFFF',
            size: n.size || 8,
        })) || [],
        links: graph?.edges.map((e: GraphEdge) => ({
            source: e.source,
            target: e.target,
            relationship: e.relationship,
            animated: e.animated,
        })) || [],
    };

    // Custom node painting
    const paintNode = useCallback((node: ForceNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
        const { x, y, label, color, size, activity_level, type } = node;
        if (x === undefined || y === undefined) return;

        const nodeSize = size * (0.5 + activity_level * 0.5);
        const fontSize = Math.max(10 / globalScale, 3);

        // Glow effect based on activity
        if (activity_level > 0.5) {
            ctx.shadowColor = color;
            ctx.shadowBlur = 15 * activity_level;
        }

        // Draw node shape based on type
        ctx.beginPath();
        if (type === 'person') {
            ctx.arc(x, y, nodeSize, 0, 2 * Math.PI);
        } else if (type === 'task') {
            const half = nodeSize;
            ctx.moveTo(x - half, y - half);
            ctx.lineTo(x + half, y - half);
            ctx.lineTo(x + half, y + half);
            ctx.lineTo(x - half, y + half);
            ctx.closePath();
        } else if (type === 'pr') {
            const half = nodeSize;
            ctx.moveTo(x, y - half);
            ctx.lineTo(x + half, y);
            ctx.lineTo(x, y + half);
            ctx.lineTo(x - half, y);
            ctx.closePath();
        } else {
            ctx.arc(x, y, nodeSize * 0.7, 0, 2 * Math.PI);
        }

        // Fill with gradient
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, nodeSize);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, `${color}66`);
        ctx.fillStyle = gradient;
        ctx.fill();

        // Reset shadow
        ctx.shadowBlur = 0;

        // Draw label
        ctx.font = `${fontSize}px IBM Plex Mono`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillStyle = '#FFFFFF';
        ctx.fillText(label, x, y + nodeSize + 4);
    }, []);

    // Custom link painting
    const paintLink = useCallback((link: ForceLink, ctx: CanvasRenderingContext2D) => {
        const sourceNode = link.source as ForceNode;
        const targetNode = link.target as ForceNode;

        if (!sourceNode.x || !sourceNode.y || !targetNode.x || !targetNode.y) return;

        ctx.beginPath();
        ctx.moveTo(sourceNode.x, sourceNode.y);
        ctx.lineTo(targetNode.x, targetNode.y);

        // Color based on relationship
        const relationshipColors: Record<string, string> = {
            BLOCKED_BY: '#FF4757',
            ASSIGNED_TO: '#00F0FF',
            DISCUSSING: '#9D4EDD',
            COMMITTED_BY: '#FFB800',
            MERGED_BY: '#00D26A',
            LINKED_TO: '#00F0FF',
            MENTIONS: '#9D4EDD',
        };

        ctx.strokeStyle = relationshipColors[link.relationship] || '#3D3D3D';
        ctx.lineWidth = link.animated ? 2 : 1;

        if (link.animated) {
            ctx.setLineDash([4, 4]);
        } else {
            ctx.setLineDash([]);
        }

        ctx.stroke();
    }, []);

    // Fit graph to view on load
    useEffect(() => {
        if (graphRef.current && graph?.nodes.length) {
            setTimeout(() => {
                graphRef.current?.zoomToFit(400, 50);
            }, 500);
        }
    }, [graph]);

    // Get container dimensions
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

    useEffect(() => {
        const updateDimensions = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight,
                });
            }
        };

        updateDimensions();
        window.addEventListener('resize', updateDimensions);
        return () => window.removeEventListener('resize', updateDimensions);
    }, []);

    return (
        <motion.div
            ref={containerRef}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="relative w-full h-full glass rounded-xl border border-obsidian-600 overflow-hidden"
        >
            {/* Header */}
            <div className="absolute top-0 left-0 right-0 z-10 px-4 py-3 border-b border-obsidian-600 bg-obsidian-800/50">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="font-display font-bold text-sm text-neon-cyan">Work Graph</h2>
                        <p className="text-xs text-gray-500 font-mono">
                            {graph ? `${graph.nodes.length} nodes, ${graph.edges.length} edges` : 'Loading...'}
                        </p>
                    </div>
                    <div className="flex items-center gap-4 text-xs font-mono">
                        <div className="flex items-center gap-1.5">
                            <div className="w-2.5 h-2.5 rounded-full bg-neon-cyan" />
                            <span className="text-gray-400">Person</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <div className="w-2.5 h-2.5 bg-neon-amber" />
                            <span className="text-gray-400">Task</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <div className="w-2.5 h-2.5 rotate-45 bg-[#FF6B6B]" />
                            <span className="text-gray-400">PR</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Graph Canvas */}
            {loading ? (
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                        <div className="w-12 h-12 border-4 border-obsidian-600 border-t-neon-cyan rounded-full animate-spin mx-auto mb-4" />
                        <p className="font-mono text-sm text-gray-500">Building Work Graph...</p>
                    </div>
                </div>
            ) : (
                <div className="pt-14">
                    <ForceGraph2D
                        ref={graphRef}
                        graphData={graphData}
                        width={dimensions.width}
                        height={dimensions.height - 56}
                        backgroundColor="transparent"
                        nodeCanvasObject={paintNode}
                        linkCanvasObject={paintLink}
                        nodePointerAreaPaint={(node: ForceNode, color, ctx) => {
                            if (node.x === undefined || node.y === undefined) return;
                            ctx.beginPath();
                            ctx.arc(node.x, node.y, node.size * 1.5, 0, 2 * Math.PI);
                            ctx.fillStyle = color;
                            ctx.fill();
                        }}
                        onNodeClick={(node) => {
                            if (onNodeClick) {
                                onNodeClick(node as unknown as GraphNode);
                            }
                        }}
                        cooldownTicks={100}
                        linkDirectionalArrowLength={4}
                        linkDirectionalArrowRelPos={1}
                        d3VelocityDecay={0.3}
                    />
                </div>
            )}
        </motion.div>
    );
}

// Add missing import
import { useState } from 'react';
