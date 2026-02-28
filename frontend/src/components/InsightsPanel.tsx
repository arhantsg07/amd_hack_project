import { motion } from 'framer-motion';
import { AlertTriangle, Users, GitPullRequest, MessageSquare, ChevronRight } from 'lucide-react';
import type { InsightsReport } from '../services/api';

interface InsightsPanelProps {
    insights: InsightsReport | null;
    loading: boolean;
}

const SeverityBadge = ({ severity }: { severity: string }) => {
    const colors: Record<string, string> = {
        critical: 'bg-red-500/20 text-red-400 border-red-500/30',
        high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
        medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
        low: 'bg-green-500/20 text-green-400 border-green-500/30',
    };

    return (
        <span className={`px-1.5 py-0.5 text-xs font-mono rounded border ${colors[severity] || colors.low}`}>
            {severity}
        </span>
    );
};

export default function InsightsPanel({ insights, loading }: InsightsPanelProps) {
    if (loading) {
        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass rounded-xl border border-obsidian-600 p-6"
            >
                <div className="flex items-center justify-center py-8">
                    <div className="w-8 h-8 border-3 border-obsidian-600 border-t-neon-amber rounded-full animate-spin" />
                </div>
            </motion.div>
        );
    }

    if (!insights) return null;

    const sections = [
        {
            title: 'Bottlenecks',
            icon: <AlertTriangle className="w-4 h-4" />,
            color: 'text-status-danger',
            bgColor: 'from-red-900/20 to-transparent',
            items: insights.bottlenecks.slice(0, 3),
            renderItem: (item: typeof insights.bottlenecks[0]) => (
                <div key={item.task_id} className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                        <p className="font-mono text-sm text-white truncate">{item.task_id}</p>
                        <p className="text-xs text-gray-500 truncate">{item.description}</p>
                    </div>
                    <SeverityBadge severity={item.severity} />
                </div>
            ),
        },
        {
            title: 'Overload Risk',
            icon: <Users className="w-4 h-4" />,
            color: 'text-status-warning',
            bgColor: 'from-amber-900/20 to-transparent',
            items: insights.overload_scores.filter(s => s.risk_level !== 'low').slice(0, 3),
            renderItem: (item: typeof insights.overload_scores[0]) => (
                <div key={item.person_id} className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-neon-cyan/20 flex items-center justify-center">
                            <span className="text-xs font-bold text-neon-cyan">
                                {item.person_name.split(' ').map(n => n[0]).join('')}
                            </span>
                        </div>
                        <div>
                            <p className="font-mono text-sm text-white">{item.person_name}</p>
                            <p className="text-xs text-gray-500">{item.task_count} tasks, ratio: {item.overload_ratio}</p>
                        </div>
                    </div>
                    <SeverityBadge severity={item.risk_level} />
                </div>
            ),
        },
        {
            title: 'Risks',
            icon: <GitPullRequest className="w-4 h-4" />,
            color: 'text-neon-amber',
            bgColor: 'from-amber-900/20 to-transparent',
            items: insights.risks.slice(0, 3),
            renderItem: (item: typeof insights.risks[0]) => (
                <div key={item.pr_id} className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                        <p className="font-mono text-sm text-white truncate">{item.pr_id}</p>
                        <p className="text-xs text-gray-500 truncate">{item.description}</p>
                    </div>
                    <SeverityBadge severity={item.severity} />
                </div>
            ),
        },
        {
            title: 'Shadow Tasks',
            icon: <MessageSquare className="w-4 h-4" />,
            color: 'text-purple-400',
            bgColor: 'from-purple-900/20 to-transparent',
            items: insights.shadow_tasks.slice(0, 3),
            renderItem: (item: typeof insights.shadow_tasks[0]) => (
                <div key={item.thread_id} className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                        <p className="font-mono text-sm text-white">#{item.channel}</p>
                        <p className="text-xs text-gray-500 truncate">
                            {item.message_count} messages, {item.participants.length} participants
                        </p>
                    </div>
                    <span className="px-1.5 py-0.5 text-xs font-mono rounded border bg-purple-500/20 text-purple-400 border-purple-500/30">
                        untracked
                    </span>
                </div>
            ),
        },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
        >
            {sections.map((section, idx) => (
                <motion.div
                    key={section.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * idx }}
                    className="glass rounded-xl border border-obsidian-600 overflow-hidden"
                >
                    {/* Header */}
                    <div className={`px-4 py-3 bg-gradient-to-r ${section.bgColor} border-b border-obsidian-600`}>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <span className={section.color}>{section.icon}</span>
                                <h3 className="font-display font-bold text-sm text-white">{section.title}</h3>
                            </div>
                            <span className={`text-xs font-mono ${section.color}`}>
                                {section.items.length}
                            </span>
                        </div>
                    </div>

                    {/* Items */}
                    <div className="p-4 space-y-3">
                        {section.items.length > 0 ? (
                            section.items.map((item) => section.renderItem(item))
                        ) : (
                            <p className="text-xs text-gray-500 text-center py-2">No issues detected</p>
                        )}
                    </div>
                </motion.div>
            ))}
        </motion.div>
    );
}
