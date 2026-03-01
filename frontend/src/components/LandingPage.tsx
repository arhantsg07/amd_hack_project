import { motion } from 'framer-motion';
import { LayoutDashboard, LogIn, UserPlus, User, ChevronRight } from 'lucide-react';

interface LandingPageProps {
    onNavigate: (view: 'landing' | 'dashboard') => void;
}

export default function LandingPage({ onNavigate }: LandingPageProps) {
    // Mock logged-in user
    const user = {
        name: 'Alex Chen',
        avatar: 'AC',
        role: 'Senior Developer'
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center px-6 relative overflow-hidden">
            {/* Background elements are handled by index.css (mesh gradient + noise) */}

            {/* Hero Section */}
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="z-10 text-center space-y-8 max-w-3xl"
            >
                {/* Logo */}
                <div className="flex flex-col items-center gap-4">
                    <motion.div
                        initial={{ rotate: -10 }}
                        animate={{ rotate: 0 }}
                        className="w-20 h-20 rounded-2xl bg-gradient-to-br from-neon-cyan to-neon-amber flex items-center justify-center glow-cyan shadow-2xl"
                    >
                        <span className="text-obsidian-900 font-display font-bold text-3xl">N</span>
                    </motion.div>
                    <div className="space-y-1">
                        <h1 className="font-display font-bold text-6xl text-white tracking-tight">
                            Nexus<span className="text-neon-cyan">Graph</span>
                        </h1>
                        <p className="text-gray-500 font-mono text-sm uppercase tracking-[0.2em]">
                            Cross-Tool Intelligence Layer
                        </p>
                    </div>
                </div>

                <p className="text-gray-400 text-lg leading-relaxed max-w-xl mx-auto">
                    Aggregate signals from Slack, Jira, and GitHub into a unified Work Graph.
                    Identify bottlenecks, track overload, and predict risks with local AI.
                </p>

                {/* User Status / Auth Buttons */}
                <div className="pt-4 flex flex-col items-center gap-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="flex items-center gap-4 px-5 py-3 glass rounded-2xl border border-obsidian-600"
                    >
                        <div className="w-10 h-10 rounded-full bg-neon-cyan/20 flex items-center justify-center border border-neon-cyan/30">
                            <User className="w-5 h-5 text-neon-cyan" />
                        </div>
                        <div className="text-left">
                            <p className="text-white font-medium text-sm leading-none">{user.name}</p>
                            <p className="text-gray-500 text-xs mt-1 font-mono">{user.role}</p>
                        </div>
                        <div className="ml-4 flex gap-2">
                            <button className="p-2 hover:bg-obsidian-600 rounded-lg transition-colors text-gray-400 hover:text-white" title="Login">
                                <LogIn className="w-4 h-4" />
                            </button>
                            <button className="p-2 hover:bg-obsidian-600 rounded-lg transition-colors text-gray-400 hover:text-white" title="Sign Up">
                                <UserPlus className="w-4 h-4" />
                            </button>
                        </div>
                    </motion.div>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => onNavigate('dashboard')}
                        className="group flex items-center gap-3 px-8 py-4 bg-neon-cyan text-obsidian-900 font-display font-bold rounded-xl glow-cyan transition-all hover:brightness-110"
                    >
                        <LayoutDashboard className="w-5 h-5" />
                        <span>Go to Dashboard</span>
                        <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </motion.button>
                </div>
            </motion.div>

            {/* Decorative Accents */}
            <div className="absolute top-1/4 -left-10 w-64 h-64 bg-neon-cyan/5 rounded-full blur-[120px]" />
            <div className="absolute bottom-1/4 -right-10 w-64 h-64 bg-neon-amber/5 rounded-full blur-[120px]" />

            {/* Footer Info */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                className="absolute bottom-8 text-gray-600 font-mono text-[10px] uppercase tracking-widest"
            >
                System Status: Optimal | Enterprise Grade Workflow Intelligence
            </motion.div>
        </div>
    );
}
