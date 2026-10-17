import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import gsap from 'gsap'
import './intro.css'

const BASE = import.meta.env.BASE_URL
const VIDEO = `${BASE}intro/`

// The camera lands (and the wall has bloomed to pure white) at 2.6 s
// (blender/terrace.py GLIDE_LAND / BLOOM): that is when the page takes over.
const LAND_AT = 2.6
// If the video hasn't started by then (slow network, Low Power Mode), go
// straight to the page instead of showing a frozen first frame.
const STALL_MS = 4000

const portraitQuery = matchMedia('(max-aspect-ratio: 1/1)')
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches
const saveData = navigator.connection?.saveData === true
// ?debug shows why the intro skipped to the page, and the screen measurements
const debug = new URLSearchParams(location.search).has('debug')

// Edge to edge on iPhone. Safari on iOS 26 never draws pinned (position: fixed)
// content behind the status bar or the floating toolbar; it paints a flat colour
// there instead (the white bands). Ordinary page content does show through both
// bars, so the intro is a normal block, taller than the screen by a "runway"
// above and below, and the page starts scrolled down by the top runway: then the
// status bar sits over the top runway and the toolbar over the bottom one.
// (?bleed forces this layout in any browser, for testing the maths on a desktop)
const isIOS = /iP(hone|ad|od)/.test(navigator.userAgent) ||
  (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1) ||
  new URLSearchParams(location.search).has('bleed')
const RUNWAY_TOP = isIOS ? 120 : 0
const RUNWAY_BOTTOM = isIOS ? 220 : 0
// the split of the hidden strips between status bar and toolbar is unknown, so
// the picture covers the physical screen plus this margin
const COVER_MARGIN = isIOS ? 40 : 0

/**
 * Sizes the page for full-bleed (see RUNWAY_TOP) and starts it scrolled to the
 * runway. If the browser won't scroll there, the top runway is dropped so the
 * picture still lines up (the worst case is a plain strip behind the clock).
 */
function useFullBleed(orientation) {
  const [measured, setMeasured] = useState('')
  useLayoutEffect(() => {
    const root = document.documentElement
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual'
    const apply = () => {
      const vh = window.innerHeight
      // iOS reports screen.width/height in portrait terms whatever the rotation
      const [short, long] = [screen.width, screen.height].sort((a, b) => a - b)
      const physical = isIOS ? (orientation === 'portrait' ? long : short) : vh
      let top = RUNWAY_TOP
      root.style.setProperty('--vh', `${vh}px`)
      root.style.setProperty('--runway-top', `${top}px`)
      root.style.setProperty('--runway-bottom', `${RUNWAY_BOTTOM}px`)
      root.style.setProperty('--cover-h', `${Math.max(vh, physical) + COVER_MARGIN}px`)
      window.scrollTo(0, top)
      if (top && Math.abs(window.scrollY - top) > 2) {
        top = 0
        root.style.setProperty('--runway-top', '0px')
        window.scrollTo(0, 0)
      }
      setMeasured(`view ${vh} · screen ${physical} · runway ${top} · scrolled ${Math.round(window.scrollY)}`)
    }
    apply()
    window.addEventListener('resize', apply)
    return () => window.removeEventListener('resize', apply)
  }, [orientation])

  // one screen, nothing to scroll: keep swipes from dragging the runway into view
  useEffect(() => {
    const block = (e) => e.preventDefault()
    window.addEventListener('touchmove', block, { passive: false })
    window.addEventListener('wheel', block, { passive: false })
    return () => {
      window.removeEventListener('touchmove', block)
      window.removeEventListener('wheel', block)
    }
  }, [])
  return measured
}

function useOrientation() {
  const [portrait, setPortrait] = useState(portraitQuery.matches)
  useEffect(() => {
    const update = () => setPortrait(portraitQuery.matches)
    portraitQuery.addEventListener('change', update)
    return () => portraitQuery.removeEventListener('change', update)
  }, [])
  return portrait ? 'portrait' : 'landscape'
}

export default function Intro() {
  const orientation = useOrientation()
  const measured = useFullBleed(orientation)
  // the video is picked once, for the screen shape at load
  const [videoOrientation] = useState(orientation)
  const [landed, setLanded] = useState(reducedMotion || saveData)
  const [videoDone, setVideoDone] = useState(reducedMotion || saveData)
  const [why, setWhy] = useState(
    reducedMotion ? 'reduce motion is on' : saveData ? 'data saver is on' : 'playing')
  const video = useRef(null)
  const stage = useRef(null)

  const finish = (reason) => {
    setWhy((current) => (current === 'playing' ? reason : current))
    setLanded(true)
    setVideoDone(true)
  }

  // play, and hand over to the page when the camera lands
  useEffect(() => {
    const v = video.current
    if (!v) return
    let frame
    const watch = () => {
      if (v.currentTime >= LAND_AT) return setLanded(true)
      frame = requestAnimationFrame(watch)
    }
    // phones only autoplay video that is muted as an attribute, not just a property
    v.muted = v.defaultMuted = true
    v.setAttribute('muted', '')
    v.play().then(watch, (e) => finish(`play() refused: ${e.name}`))
    const stall = setTimeout(
      () => v.currentTime < 0.1 && finish(`no frame after ${STALL_MS / 1000}s (readyState ${v.readyState})`),
      STALL_MS)
    const failed = () => finish(`video error ${v.error?.code}`)
    v.addEventListener('error', failed)
    return () => {
      cancelAnimationFrame(frame)
      clearTimeout(stall)
      v.removeEventListener('error', failed)
    }
  }, [])

  // turning the phone mid-intro skips to the page, laid out for the new shape
  useEffect(() => {
    if (orientation !== videoOrientation) finish('screen rotated')
  }, [orientation, videoOrientation])

  // the page's only motion: the words and button appear once the screen is white
  useLayoutEffect(() => {
    if (!landed || reducedMotion) return
    const ctx = gsap.context(() => {
      gsap.from('.details', { opacity: 0, duration: 0.9, ease: 'power2.out' })
    }, stage)
    return () => ctx.revert()
  }, [landed])

  return (
    <main className={`intro ${orientation}`}>
      <div className="stage" ref={stage}>
        {/* sits exactly where the logo lands in the video, so the handover is invisible */}
        <h1 className="mark">
          <img src={`${BASE}exxy-logo.svg`} alt="EXXY" />
        </h1>

        {!videoDone && orientation === videoOrientation && (
          <video
            ref={video}
            className="backdrop"
            src={`${VIDEO}${videoOrientation}.mp4`}
            poster={`${VIDEO}${videoOrientation}-start.jpg`}
            muted
            playsInline
            preload="auto"
            aria-hidden="true"
            onEnded={() => setVideoDone(true)}
          />
        )}

        {landed && (
          <div className="details">
            <p className="tagline">Outdoor furniture, made in Egypt since 1999.</p>
            {/* demo only: the shop isn't connected yet */}
            <button type="button" className="shop">Shop now</button>
          </div>
        )}
      </div>

      {debug && <output className="debug">{why}<br />{measured}</output>}
    </main>
  )
}
