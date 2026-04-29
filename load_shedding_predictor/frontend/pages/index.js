import Head from 'next/head'
import PredictionForm from '../components/PredictionForm'

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>LESCO Load Shedding Predictor - Tomorrow Forecast</title>
        <meta name="description" content="Forecast tomorrow's power outage hours using yesterday's actual data" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="bg-blue-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">LESCO Load Shedding Predictor</h1>
          <p className="text-blue-200 mt-2">Tomorrow’s outage forecast based on yesterday’s actual data</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Get Tomorrow’s Prediction</h2>
            <PredictionForm />
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">How it works</h2>
            <div className="space-y-4 text-gray-600">
              <p>
                This predictor uses machine learning to forecast <strong>tomorrow’s</strong> power outage hours
                based on <strong>yesterday’s actual outage hours</strong> and historical patterns.
              </p>
              <div className="bg-blue-50 rounded-lg p-4">
                <h3 className="font-medium text-blue-800 mb-2">Steps</h3>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Select your zone</li>
                  <li>Enter yesterday’s date (when you know the actual outage)</li>
                  <li>Enter the actual outage hours for that day</li>
                  <li>(Optional) Provide temperature for better accuracy</li>
                  <li>Click to get tomorrow’s predicted outage</li>
                </ul>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-800 mb-2">Confidence Levels</h3>
                <div className="flex gap-4 text-sm">
                  <div><span className="inline-block w-3 h-3 bg-green-500 rounded-full"></span> Low (0-3h)</div>
                  <div><span className="inline-block w-3 h-3 bg-yellow-500 rounded-full"></span> Medium (3-6h)</div>
                  <div><span className="inline-block w-3 h-3 bg-red-500 rounded-full"></span> High (6h+)</div>
                </div>
              </div>
              <p className="text-xs text-gray-400">
                Model uses the last 7-14 days of outage data automatically if available.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Supported Zones</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2 text-sm text-gray-600">
            {['Gulberg', 'Model Town', 'Cantt', 'Shalimar', 'Samanabad', 'Allama Iqbal Town',
              'Data Gunj Baksh', 'Ravi Road', 'Shahalam', 'Mughalpura', 'Nishtar Town', 'Johar Town',
              'Ferozewala', 'Outfall Road', 'Wahdat Colony', 'Sabzazar', 'Yunus Road', 'Cantonment',
              'Wapda Town', 'Muslim Town', 'Kahnpur', 'Shahpur', 'Harbanspura'].map(zone => (
              <div key={zone} className="bg-gray-100 rounded px-3 py-2 text-center text-xs">
                {zone}
              </div>
            ))}
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 text-gray-400 py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-sm">
          <p>LESCO Load Shedding Predictor — Tomorrow Forecast | Machine Learning with Time‑Series Analysis</p>
        </div>
      </footer>
    </div>
  )
}