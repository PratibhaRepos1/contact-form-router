const CATEGORY_STYLES = {
  sales:       { bg: '#E1F5EE', text: '#085041', label: '💼 Sales' },
  support:     { bg: '#E6F1FB', text: '#0C447C', label: '🛠 Support' },
  partnership: { bg: '#FAEEDA', text: '#633806', label: '🤝 Partnership' },
  spam:        { bg: '#FAECE7', text: '#712B13', label: '🚫 Spam' },
}

export default function ResultPanel({ result }) {
  if (!result) return null

  const style = CATEGORY_STYLES[result.category] ?? CATEGORY_STYLES.sales

  return (
    <div
      className="mt-6 rounded-xl p-5 border border-slate-200"
      style={{ backgroundColor: style.bg, color: style.text }}
    >
      <div className="flex items-center justify-between">
        <span className="text-lg font-semibold">{style.label}</span>
        <span className="text-xs uppercase tracking-wide font-medium opacity-80">
          confidence: {result.confidence}
        </span>
      </div>

      <p className="mt-3 text-sm leading-relaxed">
        <span className="font-medium">Reasoning: </span>
        {result.reasoning}
      </p>

      <div className="mt-4 pt-3 border-t border-current/10 text-sm flex flex-wrap gap-x-6 gap-y-1">
        <span>
          <span className="font-medium">Routed to:</span> {result.routed_to}
        </span>
        <span>
          <span className="font-medium">Slack posted:</span>{' '}
          {result.slack_posted ? 'yes' : 'no (webhook not configured)'}
        </span>
      </div>
    </div>
  )
}
