import { useState } from 'react'
import axios from 'axios'
import ContactForm from './components/ContactForm.jsx'
import ResultPanel from './components/ResultPanel.jsx'

export default function App() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [showHowItWorks, setShowHowItWorks] = useState(true)

  const handleSubmit = async (formData) => {
    setStatus('loading')
    setErrorMessage('')
    setResult(null)
    try {
      const { data } = await axios.post('/api/classify', formData)
      setResult(data)
      setStatus('success')
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        'Something went wrong while classifying your message.'
      setErrorMessage(detail)
      setStatus('error')
    }
  }

  return (
    <div className="min-h-full bg-slate-50">
      <div className="mx-auto max-w-2xl px-4 py-12">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Contact Form Router</h1>
          <p className="mt-2 text-slate-600">
            AI classifies your message and routes it to the right Slack channel.
          </p>
        </header>

        <section className="mb-8 rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
          <button
            type="button"
            onClick={() => setShowHowItWorks((v) => !v)}
            aria-expanded={showHowItWorks}
            aria-controls="how-it-works-body"
            className="flex w-full items-center justify-between text-left"
          >
            <span>
              <span className="block text-lg font-semibold text-slate-900">How it works</span>
              <span className="mt-1 block text-sm text-slate-600">
                Send a message and Claude figures out where it should go — no manual triage.
              </span>
            </span>
            <span
              className={`ml-4 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-base font-bold text-slate-600 transition-transform hover:bg-slate-200 ${
                showHowItWorks ? 'rotate-180' : ''
              }`}
              aria-hidden="true"
            >
              ▾
            </span>
          </button>

          {showHowItWorks && (
            <ol id="how-it-works-body" className="mt-4 grid gap-3 sm:grid-cols-2">
              <li className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700">
                <span className="font-semibold text-slate-900">1. You write</span>
                <span className="block text-slate-600">Fill in your name, email, and message.</span>
              </li>
              <li className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700">
                <span className="font-semibold text-slate-900">2. Claude reads</span>
                <span className="block text-slate-600">The AI classifies intent: sales, support, partnership, or spam.</span>
              </li>
              <li className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700">
                <span className="font-semibold text-slate-900">3. Slack receives</span>
                <span className="block text-slate-600">Your message is posted to the matching team channel.</span>
              </li>
              <li className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700">
                <span className="font-semibold text-slate-900">4. You see why</span>
                <span className="block text-slate-600">The result panel shows the category, confidence, and reasoning.</span>
              </li>
            </ol>
          )}
        </section>

        <main className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
          <ContactForm onSubmit={handleSubmit} isLoading={status === 'loading'} />

          {status === 'error' && (
            <div className="mt-6 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800">
              {errorMessage}
            </div>
          )}

          {status === 'success' && <ResultPanel result={result} />}
        </main>

        <footer className="mt-8 text-center text-xs text-slate-400">
          Powered by Claude · FastAPI · Slack webhooks
        </footer>
      </div>
    </div>
  )
}
