import { motion } from 'framer-motion';
import { Github, Trello, MessageSquare, Wifi, WifiOff, AlertCircle } from 'lucide-react';
import type { PulseStatus, ToolPulse } from '../services/api';

interface PulseBarProps {
    pulse: PulseStatus | null;
    loading: boolean;
}

const getStatusIcon = (status: string) => {
    switch (status) {
        case 'active':
            return <Wifi className="w-3.5 h-3.5" />;
        case 'inactive':
            return <WifiOff className="w-3.5 h-3.5" />;
        case 'error':
            return <AlertCircle className="w-3.5 h-3.5" />;
        default:
            return <Wifi className="w-3.5 h-3.5" />;
    }
};

const getToolIcon = (name: string) => {
    switch (name.toLowerCase()) {
        case 'github':
            return <Github className="w-4 h-4" />;
        case 'jira':
            return <Trello className="w-4 h-4" />;
        case 'slack':
            return <MessageSquare className="w-4 h-4" />;
        default:
            return null;
    }
};

const getStatusColor = (status: string, metricValue: number) => {
    if (status === 'error') return 'text-status-danger';
    if (status === 'inactive') return 'text-gray-500';
    if (metricValue > 3) return 'text-status-warning';
    return 'text-status-active';
};

const ToolIndicator = ({ tool }: { tool: ToolPulse }) => {
    const statusColor = getStatusColor(tool.status, tool.metric_value);

    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg glass border border-obsidian-600 ${statusColor}`}
        >
            <div className="flex items-center gap-1.5">
                {getToolIcon(tool.name)}
                <span className="font-mono text-xs font-medium">{tool.name}</span>
            </div>
            <div className="w-px h-4 bg-obsidian-600" />
            <div className="flex items-center gap-1">
                {getStatusIcon(tool.status)}
                <span className="font-mono text-xs">
                    {tool.metric}: <span className="font-semibold">{tool.metric_value}</span>
                </span>
            </div>
        </motion.div>
    );
};

export default function PulseBar({ pulse, loading }: PulseBarProps) {
    return (
        <motion.header
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed top-0 left-0 right-0 z-50 px-6 py-3"
        >
            <div className="max-w-7xl mx-auto">
                <div className="flex items-center justify-between glass rounded-xl px-4 py-2 border border-obsidian-600">
                    {/* Logo */}
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-neon-cyan to-neon-amber flex items-center justify-center">
                                <span className="text-obsidian-900 font-display font-bold text-sm">N</span>
                            </div>
                            <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-status-active rounded-full animate-pulse" />
                        </div>
                        <div>
                            <h1 className="font-display font-bold text-lg text-white leading-none">
                                NexusGraph
                            </h1>
                            <p className="text-xs text-gray-500 font-mono">Command Center</p>
                        </div>
                    </div>

                    {/* Tool Status */}
                    <div className="flex items-center gap-3">
                        {loading ? (
                            <div className="flex items-center gap-2 text-gray-500">
                                <div className="w-4 h-4 border-2 border-gray-600 border-t-neon-cyan rounded-full animate-spin" />
                                <span className="font-mono text-xs">Syncing...</span>
                            </div>
                        ) : pulse ? (
                            <>
                                <ToolIndicator tool={pulse.github} />
                                <ToolIndicator tool={pulse.jira} />
                                <ToolIndicator tool={pulse.slack} />
                            </>
                        ) : (
                            <span className="text-gray-500 font-mono text-xs">No data</span>
                        )}
                    </div>

                    {/* Last Sync */}
                    <div className="flex items-center gap-2 text-gray-500">
                        <span className="font-mono text-xs">
                            Last sync: {pulse ? new Date(pulse.last_sync).toLocaleTimeString() : '--:--'}
                        </span>
                        <div className={`w-2 h-2 rounded-full ${pulse ? 'bg-status-active' : 'bg-gray-600'}`} />
                    </div>
                </div>
            </div>
        </motion.header>
    );
}
