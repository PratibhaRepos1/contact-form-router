import { useState } from 'react'
import axios from 'axios'
import ContactForm from './components/ContactForm.jsx'
import ResultPanel from './components/ResultPanel.jsx'

export default function App() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')

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
