import { useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import type { PhishingAnalysisRequest, PhishingAnalysisResponse, LiveProgress } from '../types/phishing.types'
import { analyzeEmail, createAnalysisWebSocket } from '../services/api'

export function usePhishingAnalysis() {
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState<LiveProgress | null>(null)
  const [result, setResult] = useState<PhishingAnalysisResponse | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => () => {
    wsRef.current?.close()
  }, [])

  const startWebSocket = (payload: PhishingAnalysisRequest) =>
    new Promise<void>((resolve, reject) => {
      try {
        wsRef.current = createAnalysisWebSocket(
          (data) => {
            if (data.type === 'progress') {
              setProgress(data.payload as LiveProgress)
            } else if (data.type === 'result') {
              setResult(data.payload as PhishingAnalysisResponse)
              setProgress(null)
              toast.success('Analysis complete')
              resolve()
            }
          },
          (err) => {
            console.error('WS Error', err)
            // If WS fails, we can reject, but we might want to fallback to REST?
            // For now, let's reject so the catch block handles it (which sadly just errors)
            // But technically we proceed to REST in runAnalysis if we didn't await this?
            // The logic requires this to resolve.
            reject(err)
          }
        )

        // Send payload when ready
        const sendPayload = () => {
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(payload))
          }
        }

        if (wsRef.current.readyState === WebSocket.OPEN) {
          sendPayload()
        } else {
          wsRef.current.addEventListener('open', sendPayload)
        }

      } catch (err) {
        reject(err)
      }
    })

  const runAnalysis = async (payload: PhishingAnalysisRequest) => {
    setLoading(true)
    setResult(null)
    setProgress({ step: 'Queued', percent: 0 })
    try {
      // Try WebSocket first
      await startWebSocket(payload)

      // Note: original code called analyzeEmail(payload) AFTER WebSocket resolved.
      // This seems redundant if WS returns the result. 
      // However, if WS is just for progress and result comes from there, we are good.
      // If WS is PURELY for progress and we MUST call REST for result, then startWebSocket shouldn't resolve on result.
      // BUT current backend sends 'result' type on WS.
      // So we have the result.

      // If we want to be safe and follow original flow (maybe WS result is partial?):
      // const restRes = await analyzeEmail(payload)
      // setResult(restRes)

    } catch (err: any) {
      console.warn('WS failed, falling back to REST', err)
      // Fallback to REST analysis if WS fails
      try {
        const restRes = await analyzeEmail(payload)
        setResult(restRes)
        setProgress(null)
      } catch (restErr: any) {
        toast.error(restErr?.message ?? 'Analysis failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return { loading, progress, result, runAnalysis, ws: wsRef.current }
}
