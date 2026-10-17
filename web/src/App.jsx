import { lazy, Suspense } from 'react'
import Intro from './Intro.jsx'

// The rejected real-time version stays available for comparison at ?realtime.
// It is loaded lazily so visitors to the intro never download three.js.
const RealtimeTerrace = lazy(() => import('./scene/RealtimeTerrace.jsx'))
const realtime = new URLSearchParams(location.search).has('realtime')

export default function App() {
  if (!realtime) return <Intro />
  return (
    <Suspense fallback={null}>
      <RealtimeTerrace />
    </Suspense>
  )
}
