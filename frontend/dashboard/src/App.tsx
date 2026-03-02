import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import MarketOverview from '@/pages/MarketOverview'
import StockChart from '@/pages/StockChart'
import FactorExplorer from '@/pages/FactorExplorer'
import BacktestViewer from '@/pages/BacktestViewer'
import PortfolioAnalyzer from '@/pages/PortfolioAnalyzer'

const navItems = [
  { to: '/', label: 'Market Overview' },
  { to: '/charts', label: 'Charts' },
  { to: '/factors', label: 'Factors' },
  { to: '/backtest', label: 'Backtest' },
  { to: '/portfolio', label: 'Portfolio' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950 text-gray-100">
        {/* Top Navigation */}
        <nav className="bg-gray-900 border-b border-gray-800 px-6 py-3">
          <div className="flex items-center gap-8">
            <span className="text-orange-500 font-bold text-lg tracking-wide">
              ⬡ BQUANT
            </span>
            <div className="flex gap-6 text-sm">
              {navItems.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    isActive
                      ? 'text-orange-400 font-medium border-b border-orange-400 pb-0.5'
                      : 'text-gray-400 hover:text-gray-200 transition-colors'
                  }
                >
                  {label}
                </NavLink>
              ))}
            </div>
            <a
              href={`${import.meta.env.VITE_JUPYTER_URL ?? 'http://localhost:8888'}/jupyter`}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-auto text-xs text-gray-500 hover:text-gray-300 border border-gray-700 px-3 py-1 rounded transition-colors"
            >
              Open JupyterLab →
            </a>
          </div>
        </nav>

        {/* Page Content */}
        <main className="p-6">
          <Routes>
            <Route path="/" element={<MarketOverview />} />
            <Route path="/charts" element={<StockChart />} />
            <Route path="/factors" element={<FactorExplorer />} />
            <Route path="/backtest" element={<BacktestViewer />} />
            <Route path="/portfolio" element={<PortfolioAnalyzer />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
