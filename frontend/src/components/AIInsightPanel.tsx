import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Send, Cpu, Sparkles, X } from 'lucide-react';
import { chatWithGraph, ChatResponse } from '../services/api';

interface Message {
    id: string;
    type: 'user' | 'ai';
    content: string;
    timestamp: Date;
    sources?: string[];
    confidence?: number;
}

interface AIInsightPanelProps {
    localInferenceMode: boolean;
    onToggleLocalMode: () => void;
}

export default function AIInsightPanel({ localInferenceMode, onToggleLocalMode }: AIInsightPanelProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '0',
            type: 'ai',
            content: '🤖 **NexusGraph AI Assistant**\n\nI can help you understand your work graph. Try asking:\n\n• "What is blocking NEXUS-100?"\n• "Show me bottlenecks"\n• "Who is overloaded?"\n• "Give me a brief"',
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            type: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        try {
            const response: ChatResponse = await chatWithGraph(input);

            // Simulate typing delay for effect
            await new Promise((resolve) => setTimeout(resolve, 500));

            const aiMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'ai',
                content: response.response,
                timestamp: new Date(),
                sources: response.sources,
                confidence: response.confidence,
            };

            setMessages((prev) => [...prev, aiMessage]);
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'ai',
                content: '❌ Failed to get response. Please check if the backend is running.',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsTyping(false);
        }
    };

    const formatContent = (content: string) => {
        // Simple markdown-like formatting
        return content
            .replace(/\*\*(.+?)\*\*/g, '<strong class="text-neon-cyan">$1</strong>')
            .replace(/`(.+?)`/g, '<code class="px-1 py-0.5 bg-obsidian-600 rounded text-neon-amber">$1</code>')
            .replace(/•/g, '<span class="text-neon-amber">›</span>')
            .replace(/\n/g, '<br/>');
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col h-full glass rounded-xl border border-obsidian-600 overflow-hidden"
        >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-obsidian-600 bg-obsidian-800/50">
                <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-neon-cyan" />
                    <h2 className="font-display font-bold text-sm text-white">AI Insights</h2>
                </div>

                {/* Local Inference Toggle */}
                <button
                    onClick={onToggleLocalMode}
                    className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-mono transition-all ${localInferenceMode
                            ? 'bg-gradient-to-r from-orange-600 to-red-600 text-white'
                            : 'bg-obsidian-700 text-gray-400 hover:text-white'
                        }`}
                >
                    <Cpu className="w-3 h-3" />
                    <span>Local NPU</span>
                </button>
            </div>

            {/* AMD Badge */}
            <AnimatePresence>
                {localInferenceMode && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="px-4 py-2 bg-gradient-to-r from-orange-900/30 to-red-900/30 border-b border-orange-700/30"
                    >
                        <div className="flex items-center justify-center gap-2 text-xs">
                            <Sparkles className="w-3 h-3 text-orange-400" />
                            <span className="font-mono text-orange-300">
                                Powered by AMD Ryzen™ AI
                            </span>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
                <AnimatePresence>
                    {messages.map((message, index) => (
                        <motion.div
                            key={message.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[85%] rounded-lg px-3 py-2 ${message.type === 'user'
                                        ? 'bg-neon-cyan/20 border border-neon-cyan/30'
                                        : 'bg-obsidian-700 border border-obsidian-600'
                                    }`}
                            >
                                <div
                                    className="text-sm font-mono leading-relaxed text-gray-200 glitch-hover"
                                    dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
                                />
                                {message.sources && message.sources.length > 0 && (
                                    <div className="mt-2 pt-2 border-t border-obsidian-600 text-xs text-gray-500">
                                        Sources: {message.sources.join(', ')}
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {/* Typing Indicator */}
                <AnimatePresence>
                    {isTyping && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex items-center gap-2 text-gray-500"
                        >
                            <div className="flex gap-1">
                                <span className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <span className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <span className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                            <span className="text-xs font-mono">Analyzing graph...</span>
                        </motion.div>
                    )}
                </AnimatePresence>

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-3 border-t border-obsidian-600 bg-obsidian-800/50">
                <div className="flex items-center gap-2">
                    <span className="text-neon-cyan font-mono text-sm">❯</span>
                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about your work graph..."
                        className="flex-1 bg-transparent border-none outline-none text-sm font-mono text-white placeholder-gray-600"
                        disabled={isTyping}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isTyping}
                        className="p-2 rounded-lg bg-neon-cyan/20 text-neon-cyan hover:bg-neon-cyan/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </form>
        </motion.div>
    );
}
