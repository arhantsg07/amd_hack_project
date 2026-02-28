/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Obsidian Industrial Theme
                obsidian: {
                    900: '#0D0D0D',
                    800: '#141414',
                    700: '#1A1A1A',
                    600: '#242424',
                    500: '#2E2E2E',
                    400: '#3D3D3D',
                },
                neon: {
                    amber: '#FFB800',
                    'amber-dim': '#CC9300',
                    cyan: '#00F0FF',
                    'cyan-dim': '#00C4CC',
                },
                status: {
                    active: '#00F0FF',
                    warning: '#FFB800',
                    danger: '#FF4757',
                    success: '#00D26A',
                }
            },
            fontFamily: {
                mono: ['IBM Plex Mono', 'monospace'],
                display: ['Syne', 'sans-serif'],
                sans: ['Inter', 'sans-serif'],
            },
            backgroundImage: {
                'mesh-gradient': 'radial-gradient(at 40% 20%, hsla(180, 100%, 50%, 0.08) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(45, 100%, 50%, 0.06) 0px, transparent 50%), radial-gradient(at 0% 50%, hsla(280, 100%, 50%, 0.04) 0px, transparent 50%), radial-gradient(at 80% 50%, hsla(180, 100%, 50%, 0.05) 0px, transparent 50%), radial-gradient(at 0% 100%, hsla(45, 100%, 50%, 0.05) 0px, transparent 50%)',
            },
            keyframes: {
                'pulse-glow': {
                    '0%, 100%': { boxShadow: '0 0 20px rgba(0, 240, 255, 0.3)' },
                    '50%': { boxShadow: '0 0 40px rgba(0, 240, 255, 0.6)' },
                },
                'flow': {
                    '0%': { strokeDashoffset: '24' },
                    '100%': { strokeDashoffset: '0' },
                },
                'glitch': {
                    '0%': { transform: 'translate(0)' },
                    '20%': { transform: 'translate(-2px, 2px)' },
                    '40%': { transform: 'translate(-2px, -2px)' },
                    '60%': { transform: 'translate(2px, 2px)' },
                    '80%': { transform: 'translate(2px, -2px)' },
                    '100%': { transform: 'translate(0)' },
                },
                'typing': {
                    'from': { width: '0' },
                    'to': { width: '100%' },
                },
            },
            animation: {
                'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
                'flow': 'flow 1s linear infinite',
                'glitch': 'glitch 0.3s ease-in-out',
                'typing': 'typing 2s steps(40, end)',
            },
        },
    },
    plugins: [],
}
