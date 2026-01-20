import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Activity, AlertTriangle, TrendingUp, TrendingDown, BarChart3, Play, Pause, Trash2 } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

const DarkPoolDashboard = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [trades, setTrades] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [alertHistory, setAlertHistory] = useState([]);
  const [summary, setSummary] = useState({});
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [symbolAnalytics, setSymbolAnalytics] = useState({});
  const [activeTab, setActiveTab] = useState('monitoring');
  
  const priceChartRef = useRef(null);
  const volumeChartRef = useRef(null);
  const buysellChartRef = useRef(null);
  const alertTimelineRef = useRef(null);

  // Fetch data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tradesRes, alertsRes, summaryRes, historyRes] = await Promise.all([
          fetch(`${API_BASE_URL}/trades?limit=100`),
          fetch(`${API_BASE_URL}/alerts`),
          fetch(`${API_BASE_URL}/analytics/summary`),
          fetch(`${API_BASE_URL}/alerts/history?limit=30`)
        ]);

        if (tradesRes.ok) setTrades(await tradesRes.json());
        if (alertsRes.ok) setAlerts(await alertsRes.json());
        if (summaryRes.ok) setSummary(await summaryRes.json());
        if (historyRes.ok) setAlertHistory(await historyRes.json());
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  // Fetch symbol analytics
  useEffect(() => {
    const fetchSymbolData = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/analytics/symbol/${selectedSymbol}`);
        if (res.ok) setSymbolAnalytics(await res.json());
      } catch (error) {
        console.error('Error fetching symbol analytics:', error);
      }
    };

    if (selectedSymbol) {
      fetchSymbolData();
      const interval = setInterval(fetchSymbolData, 1000);
      return () => clearInterval(interval);
    }
  }, [selectedSymbol]);

  // D3 Price Chart
  useEffect(() => {
    if (!priceChartRef.current || trades.length === 0) return;

    const symbolTrades = trades.filter(t => t.symbol === selectedSymbol).slice(-50);
    if (symbolTrades.length === 0) return;

    const margin = { top: 20, right: 80, bottom: 50, left: 60 };
    const width = 700 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    d3.select(priceChartRef.current).selectAll("*").remove();

    const svg = d3.select(priceChartRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear()
      .domain([0, symbolTrades.length - 1])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([d3.min(symbolTrades, d => d.price) * 0.99, d3.max(symbolTrades, d => d.price) * 1.01])
      .range([height, 0]);

    const line = d3.line()
      .x((d, i) => x(i))
      .y(d => y(d.price))
      .curve(d3.curveMonotoneX);

    svg.append("path")
      .datum(symbolTrades)
      .attr("fill", "none")
      .attr("stroke", "#2196F3")
      .attr("stroke-width", 2)
      .attr("d", line);

    svg.selectAll(".dot")
      .data(symbolTrades)
      .enter().append("circle")
      .attr("cx", (d, i) => x(i))
      .attr("cy", d => y(d.price))
      .attr("r", d => Math.sqrt(d.quantity) / 3)
      .attr("fill", d => d.side === "BUY" ? "#4CAF50" : "#f44336")
      .attr("opacity", 0.6);

    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(10));

    svg.append("g")
      .call(d3.axisLeft(y).tickFormat(d => `$${d.toFixed(2)}`));

    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -5)
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .attr("font-weight", "bold")
      .text(`${selectedSymbol} Price Movement`);
  }, [trades, selectedSymbol]);

  // D3 Volume Chart
  useEffect(() => {
    if (!volumeChartRef.current || trades.length === 0) return;

    const volumeData = d3.rollup(
      trades,
      v => d3.sum(v, d => d.quantity),
      d => d.symbol
    );
    const data = Array.from(volumeData, ([symbol, volume]) => ({ symbol, volume }));

    const margin = { top: 30, right: 30, bottom: 70, left: 80 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    d3.select(volumeChartRef.current).selectAll("*").remove();

    const svg = d3.select(volumeChartRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
      .domain(data.map(d => d.symbol))
      .range([0, width])
      .padding(0.2);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.volume) * 1.1])
      .range([height, 0]);

    svg.selectAll(".bar")
      .data(data)
      .enter().append("rect")
      .attr("x", d => x(d.symbol))
      .attr("y", d => y(d.volume))
      .attr("width", x.bandwidth())
      .attr("height", d => height - y(d.volume))
      .attr("fill", "#2196F3")
      .attr("opacity", 0.8);

    svg.selectAll(".label")
      .data(data)
      .enter().append("text")
      .attr("x", d => x(d.symbol) + x.bandwidth() / 2)
      .attr("y", d => y(d.volume) - 5)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .text(d => d.volume.toLocaleString());

    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x));

    svg.append("g")
      .call(d3.axisLeft(y).tickFormat(d => d.toLocaleString()));

    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -10)
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .attr("font-weight", "bold")
      .text("Volume Distribution");
  }, [trades]);

  // API Controls
  const toggleSurveillance = async () => {
    const endpoint = isRunning ? 'stop' : 'start';
    try {
      const res = await fetch(`${API_BASE_URL}/${endpoint}`, { method: 'POST' });
      if (res.ok) setIsRunning(!isRunning);
    } catch (error) {
      console.error('Error toggling surveillance:', error);
    }
  };

  const clearData = async () => {
    try {
      await fetch(`${API_BASE_URL}/clear`, { method: 'POST' });
      setTrades([]);
      setAlerts([]);
      setAlertHistory([]);
      setSummary({});
    } catch (error) {
      console.error('Error clearing data:', error);
    }
  };

  const getSeverityColor = (severity) => {
    return severity === 'HIGH' ? 'text-red-600' : severity === 'MEDIUM' ? 'text-orange-600' : 'text-green-600';
  };

  const getSeverityBg = (severity) => {
    return severity === 'HIGH' ? 'bg-red-100' : severity === 'MEDIUM' ? 'bg-orange-100' : 'bg-green-100';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <Activity className="w-8 h-8" />
          Dark Pool Trading Surveillance
        </h1>
        <p className="text-gray-600">Real-time monitoring and forensic analysis</p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSurveillance}
            className={`flex items-center gap-2 px-6 py-2 rounded-lg font-semibold ${
              isRunning ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'
            } text-white transition`}
          >
            {isRunning ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
            {isRunning ? 'Stop' : 'Start'} Surveillance
          </button>
          
          <button
            onClick={clearData}
            className="flex items-center gap-2 px-6 py-2 rounded-lg font-semibold bg-gray-600 hover:bg-gray-700 text-white transition"
          >
            <Trash2 className="w-5 h-5" />
            Clear Data
          </button>

          <div className="ml-auto flex gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{summary.total_trades || 0}</div>
              <div className="text-sm text-gray-600">Total Trades</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{(summary.total_volume || 0).toLocaleString()}</div>
              <div className="text-sm text-gray-600">Total Volume</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{alerts.length}</div>
              <div className="text-sm text-gray-600">Active Alerts</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex gap-4">
            {['monitoring', 'forensics', 'analytics'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 font-semibold capitalize ${
                  activeTab === tab
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'monitoring' && (
        <div className="grid grid-cols-2 gap-6">
          {/* Live Trades */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Live Trade Feed
            </h2>
            <div className="overflow-auto max-h-96">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-3 py-2 text-left">Symbol</th>
                    <th className="px-3 py-2 text-left">Price</th>
                    <th className="px-3 py-2 text-left">Quantity</th>
                    <th className="px-3 py-2 text-left">Side</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.slice(-15).reverse().map((trade, idx) => (
                    <tr key={idx} className="border-t">
                      <td className="px-3 py-2 font-semibold">{trade.symbol}</td>
                      <td className="px-3 py-2">${trade.price.toFixed(2)}</td>
                      <td className="px-3 py-2">{trade.quantity.toLocaleString()}</td>
                      <td className={`px-3 py-2 font-semibold ${trade.side === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                        {trade.side}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Active Alerts */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Active Alerts
            </h2>
            <div className="space-y-3 max-h-96 overflow-auto">
              {alerts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  ✅ No abnormal activity detected
                </div>
              ) : (
                alerts.slice(0, 10).map((alert, idx) => (
                  <div key={idx} className={`p-3 rounded-lg ${getSeverityBg(alert.severity)}`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <div className={`font-semibold ${getSeverityColor(alert.severity)}`}>
                          {alert.type} - {alert.symbol}
                        </div>
                        <div className="text-sm text-gray-700 mt-1">{alert.message}</div>
                        <div className="text-xs text-gray-600 mt-1">{alert.details}</div>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'forensics' && (
        <div>
          {/* Symbol Selector */}
          <div className="bg-white rounded-lg shadow p-4 mb-6">
            <label className="block text-sm font-semibold mb-2">Select Symbol for Analysis</label>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              {(summary.symbols || ['AAPL', 'TSLA', 'NVDA', 'GOOGL']).map(sym => (
                <option key={sym} value={sym}>{sym}</option>
              ))}
            </select>
          </div>

          {/* Price Chart */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Price Movement Chart</h2>
            <div ref={priceChartRef}></div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">Current Price</div>
              <div className="text-2xl font-bold">${symbolAnalytics.current_price?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">VWAP</div>
              <div className="text-2xl font-bold">${symbolAnalytics.vwap?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">Price Change</div>
              <div className={`text-2xl font-bold ${(symbolAnalytics.price_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${symbolAnalytics.price_change?.toFixed(2) || '0.00'} ({symbolAnalytics.price_change_pct || 0}%)
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">Total Volume</div>
              <div className="text-2xl font-bold">{(symbolAnalytics.total_volume || 0).toLocaleString()}</div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'analytics' && (
        <div>
          {/* Volume Chart */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Volume Distribution
            </h2>
            <div ref={volumeChartRef}></div>
          </div>

          {/* Statistics Table */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Symbol Statistics</h2>
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">Symbol</th>
                  <th className="px-4 py-2 text-left">Trades</th>
                  <th className="px-4 py-2 text-left">Volume</th>
                  <th className="px-4 py-2 text-left">Buy Volume</th>
                  <th className="px-4 py-2 text-left">Sell Volume</th>
                </tr>
              </thead>
              <tbody>
                {(summary.symbols || []).map(sym => {
                  const symTrades = trades.filter(t => t.symbol === sym);
                  const buyVol = symTrades.filter(t => t.side === 'BUY').reduce((a, b) => a + b.quantity, 0);
                  const sellVol = symTrades.filter(t => t.side === 'SELL').reduce((a, b) => a + b.quantity, 0);
                  return (
                    <tr key={sym} className="border-t">
                      <td className="px-4 py-2 font-semibold">{sym}</td>
                      <td className="px-4 py-2">{symTrades.length}</td>
                      <td className="px-4 py-2">{(buyVol + sellVol).toLocaleString()}</td>
                      <td className="px-4 py-2 text-green-600">{buyVol.toLocaleString()}</td>
                      <td className="px-4 py-2 text-red-600">{sellVol.toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default DarkPoolDashboard;