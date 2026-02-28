import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Maximize2, Minimize2 } from 'lucide-react';
import PulseBar from './PulseBar';
import GraphVisualizer from './GraphVisualizer';
import AIInsightPanel from './AIInsightPanel';
import InsightsPanel from './InsightsPanel';
import BriefPanel from './BriefPanel';
import {
    getWorkGraph,
    getPulseStatus,
    getInsights,
    getActivityBrief,
    regenerateData,
    WorkGraph,
    PulseStatus,
    InsightsReport,
    ActivityBrief,
    GraphNode,
} from '../services/api';

export default function Dashboard() {
    const [graph, setGraph] = useState<WorkGraph | null>(null);
    const [pulse, setPulse] = useState<PulseStatus | null>(null);
    const [insights, setInsights] = useState<InsightsReport | null>(null);
    const [brief, setBrief] = useState<ActivityBrief | null>(null);
    const [loading, setLoading] = useState(true);
    const [localInferenceMode, setLocalInferenceMode] = useState(false);
    const [graphExpanded, setGraphExpanded] = useState(false);
    const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

    const fetchData = async (refreshGraph = false) => {
        setLoading(true);
        try {
            const [graphData, pulseData, insightsData, briefData] = await Promise.all([
                getWorkGraph(refreshGraph),
                getPulseStatus(),
                getInsights(),
                getActivityBrief(),
            ]);
            setGraph(graphData);
            setPulse(pulseData);
            setInsights(insightsData);
            setBrief(briefData);
        } catch (error) {
            console.error('Failed to fetch data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = async () => {
        await regenerateData();
        await fetchData(true);
    };

    const handleNodeClick = (node: GraphNode) => {
        setSelectedNode(node);
        console.log('Selected node:', node);
    };

    useEffect(() => {
        fetchData();

        // Refresh pulse every 30 seconds
        const interval = setInterval(async () => {
            const pulseData = await getPulseStatus();
            setPulse(pulseData);
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen pb-8">
            {/* Pulse Bar */}
            <PulseBar pulse={pulse} loading={loading} />

            {/* Main Content */}
            <main className="pt-24 px-6">
                <div className="max-w-7xl mx-auto space-y-6">
                    {/* Title Section */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-center justify-between"
                    >
                        <div>
                            <h1 className="font-display font-bold text-2xl text-white">
                                Work Intelligence <span className="text-neon-cyan">Dashboard</span>
                            </h1>
                            <p className="text-gray-500 text-sm mt-1">
                                Cross-tool insights across Slack, Jira, and GitHub
                            </p>
                        </div>
                        <button
                            onClick={handleRefresh}
                            disabled={loading}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg glass border border-obsidian-600 text-gray-300 hover:text-white hover:border-neon-cyan/50 transition-all disabled:opacity-50"
                        >
                            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                            <span className="text-sm font-mono">Refresh Data</span>
                        </button>
                    </motion.div>

                    {/* Brief Panel */}
                    <BriefPanel brief={brief} loading={loading} />

                    {/* Insights Grid */}
                    <InsightsPanel insights={insights} loading={loading} />

                    {/* Graph + AI Panel */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Graph Visualizer */}
                        <motion.div
                            layout
                            className={`${graphExpanded ? 'lg:col-span-3' : 'lg:col-span-2'} h-[500px] relative`}
                        >
                            <button
                                onClick={() => setGraphExpanded(!graphExpanded)}
                                className="absolute top-4 right-4 z-20 p-2 rounded-lg bg-obsidian-700/80 text-gray-400 hover:text-white transition-all"
                            >
                                {graphExpanded ? (
                                    <Minimize2 className="w-4 h-4" />
                                ) : (
                                    <Maximize2 className="w-4 h-4" />
                                )}
                            </button>
                            <GraphVisualizer
                                graph={graph}
                                loading={loading}
                                onNodeClick={handleNodeClick}
                            />
                        </motion.div>

                        {/* AI Insight Panel */}
                        {!graphExpanded && (
                            <div className="h-[500px]">
                                <AIInsightPanel
                                    localInferenceMode={localInferenceMode}
                                    onToggleLocalMode={() => setLocalInferenceMode(!localInferenceMode)}
                                />
                            </div>
                        )}
                    </div>

                    {/* Selected Node Details */}
                    {selectedNode && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="glass rounded-xl border border-obsidian-600 p-4"
                        >
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="font-display font-bold text-sm text-neon-cyan">
                                    Selected: {selectedNode.label}
                                </h3>
                                <button
                                    onClick={() => setSelectedNode(null)}
                                    className="text-gray-500 hover:text-white text-sm"
                                >
                                    ✕
                                </button>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                <div>
                                    <span className="text-gray-500">Type:</span>
                                    <span className="ml-2 text-white capitalize">{selectedNode.type}</span>
                                </div>
                                <div>
                                    <span className="text-gray-500">Activity:</span>
                                    <span className="ml-2 text-white">{(selectedNode.activity_level * 100).toFixed(0)}%</span>
                                </div>
                                {Object.entries(selectedNode.metadata).slice(0, 4).map(([key, value]) => (
                                    <div key={key}>
                                        <span className="text-gray-500 capitalize">{key.replace('_', ' ')}:</span>
                                        <span className="ml-2 text-white">{String(value)}</span>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </div>
            </main>

            {/* Footer */}
            <footer className="mt-12 text-center text-xs text-gray-600 font-mono">
                <p>NexusGraph v1.0.0 | Cross-Tool Intelligence Layer</p>
            </footer>
        </div>
    );
}
