import { useState } from 'react'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'

function App() {
    const [view, setView] = useState<'landing' | 'dashboard'>('landing');

    return (
        <>
            {view === 'landing' ? (
                <LandingPage onNavigate={setView} />
            ) : (
                <Dashboard />
            )}
        </>
    )
}

export default App
