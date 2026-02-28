import { motion } from 'framer-motion';
import { Clock, MessageSquare, GitMerge, AlertTriangle, TrendingUp } from 'lucide-react';
import type { ActivityBrief } from '../services/api';

interface BriefPanelProps {
    brief: ActivityBrief | null;
    loading: boolean;
}

export default function BriefPanel({ brief, loading }: BriefPanelProps) {
    if (loading) {
        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass rounded-xl border border-obsidian-600 p-4"
            >
                <div className="animate-pulse space-y-3">
                    <div className="h-4 bg-obsidian-600 rounded w-3/4" />
                    <div className="h-3 bg-obsidian-600 rounded w-1/2" />
                </div>
            </motion.div>
        );
    }

    if (!brief) return null;

    const metrics = [
        { icon: <MessageSquare className="w-4 h-4" />, label: 'Hot Threads', value: brief.hot_threads, color: 'text-neon-cyan' },
        { icon: <AlertTriangle className="w-4 h-4" />, label: 'Blocked', value: brief.blocked_tasks, color: 'text-status-danger' },
        { icon: <GitMerge className="w-4 h-4" />, label: 'Merged PRs', value: brief.merged_prs, color: 'text-status-success' },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="glass rounded-xl border border-obsidian-600 overflow-hidden"
        >
            {/* Header */}
            <div className="px-4 py-3 border-b border-obsidian-600 bg-gradient-to-r from-neon-cyan/10 to-transparent">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-neon-cyan" />
                        <h2 className="font-display font-bold text-sm text-white">24-Hour Brief</h2>
                    </div>
                    <span className="text-xs font-mono text-gray-500">
                        {new Date(brief.period_end).toLocaleTimeString()}
                    </span>
                </div>
            </div>

            {/* Summary */}
            <div className="p-4">
                <p className="text-sm text-gray-300 leading-relaxed">{brief.summary}</p>
            </div>

            {/* Metrics */}
            <div className="px-4 pb-4">
                <div className="grid grid-cols-3 gap-3">
                    {metrics.map((metric, idx) => (
                        <motion.div
                            key={metric.label}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.1 + idx * 0.1 }}
                            className="bg-obsidian-700/50 rounded-lg p-3 text-center"
                        >
                            <div className={`flex justify-center mb-1 ${metric.color}`}>
                                {metric.icon}
                            </div>
                            <p className="text-xl font-display font-bold text-white">{metric.value}</p>
                            <p className="text-xs text-gray-500">{metric.label}</p>
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Key Updates */}
            {brief.key_updates.length > 0 && (
                <div className="px-4 pb-4">
                    <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-3.5 h-3.5 text-neon-amber" />
                        <span className="text-xs font-mono text-gray-400">Key Updates</span>
                    </div>
                    <div className="space-y-1.5">
                        {brief.key_updates.slice(0, 3).map((update, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.3 + idx * 0.1 }}
                                className="text-xs text-gray-400 font-mono flex items-start gap-2"
                            >
                                <span className="text-neon-amber">›</span>
                                <span>{update}</span>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}
        </motion.div>
    );
}
