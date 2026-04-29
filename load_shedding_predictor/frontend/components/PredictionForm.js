import { useState } from 'react'

const ZONES = [
  'Gulberg', 'Model Town', 'Cantt', 'Shalimar', 'Samanabad', 'Allama Iqbal Town',
  'Data Gunj Baksh', 'Ravi Road', 'Shahalam', 'Mughalpura', 'Outfall Road',
  'Nishtar Town', 'Wahdat Colony', 'Sabzazar', 'Yunus Road', 'Cantonment',
  'Johar Town', 'Wapda Town', 'Muslim Town', 'Kahnpur', 'Shahpur', 'Harbanspura',
  'Ferozewala'
]

export default function PredictionForm() {
  const [zone, setZone] = useState('')
  const [yesterdayDate, setYesterdayDate] = useState('')
  const [yesterdayOutage, setYesterdayOutage] = useState('')
  const [temperature, setTemperature] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setResult(null)

    if (!zone || !yesterdayDate || !yesterdayOutage) {
      setError('Please fill in zone, yesterday’s date, and yesterday’s outage hours')
      return
    }

    if (isNaN(parseFloat(yesterdayOutage)) || parseFloat(yesterdayOutage) < 0) {
      setError('Please enter a valid positive number for outage hours')
      return
    }

    setLoading(true)

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          zone,
          yesterday_date: yesterdayDate,
          yesterday_outage_hours: parseFloat(yesterdayOutage),
          temperature: temperature ? parseFloat(temperature) : null
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Prediction failed')
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'low': return 'bg-green-100 border-green-500 text-green-800'
      case 'medium': return 'bg-yellow-100 border-yellow-500 text-yellow-800'
      case 'high': return 'bg-red-100 border-red-500 text-red-800'
      default: return 'bg-gray-100 border-gray-500 text-gray-800'
    }
  }

  const getConfidenceBadge = (confidence) => {
    switch (confidence) {
      case 'low': return 'bg-green-500'
      case 'medium': return 'bg-yellow-500'
      case 'high': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Zone <span className="text-red-500">*</span>
        </label>
        <select
          value={zone}
          onChange={(e) => setZone(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        >
          <option value="">Select a zone</option>
          {ZONES.map(z => (
            <option key={z} value={z}>{z}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Yesterday’s Date <span className="text-red-500">*</span>
        </label>
        <input
          type="date"
          value={yesterdayDate}
          onChange={(e) => setYesterdayDate(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <p className="text-xs text-gray-500 mt-1">Date for which you know actual outage hours</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Yesterday’s Actual Outage Hours <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          step="0.1"
          min="0"
          value={yesterdayOutage}
          onChange={(e) => setYesterdayOutage(e.target.value)}
          placeholder="e.g., 3.5"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Temperature (°C) (optional)
        </label>
        <input
          type="number"
          step="0.1"
          value={temperature}
          onChange={(e) => setTemperature(e.target.value)}
          placeholder="e.g., 25"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p className="text-xs text-gray-500 mt-1">Used for better accuracy</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {result && (
        <div className={`border-l-4 p-4 rounded ${getConfidenceColor(result.confidence)}`}>
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold">Tomorrow’s Prediction</h3>
            <span className={`px-2 py-1 text-xs text-white rounded ${getConfidenceBadge(result.confidence)}`}>
              {result.confidence.toUpperCase()} CONFIDENCE
            </span>
          </div>
          <div className="text-3xl font-bold text-gray-800">
            {result.predicted_outage_hours} hours
          </div>
          <p className="text-sm text-gray-600 mt-1">
            For {result.zone} on {result.prediction_for_date}
          </p>
          {result.used_features && (
            <details className="mt-2 text-xs text-gray-500">
              <summary>Show technical details</summary>
              <pre className="mt-1 overflow-x-auto">{JSON.stringify(result.used_features, null, 2)}</pre>
            </details>
          )}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors font-medium"
      >
        {loading ? 'Predicting...' : 'Predict Tomorrow\'s Outage'}
      </button>
    </form>
  )
}