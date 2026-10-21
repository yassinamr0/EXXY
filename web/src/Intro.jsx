import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import gsap from 'gsap'
import './intro.css'

const BASE = import.meta.env.BASE_URL
const VIDEO = `${BASE}intro/`

// The camera lands (and the wall has bloomed to pure white) at 2.6 s
// (blender/terrace.py GLIDE_LAND / BLOOM): that is when the page takes over.
const LAND_AT = 2.6
// Play automatically. If playback is blocked or cannot start, show the page.
// No visible progress this long after asking to play: show the page.
const START_MS = 2500
// Buffering this long (visible tab only, reset whenever playback advances):
// give up and show the page.
const STALL_MS = 12000

const portraitQuery = matchMedia('(max-aspect-ratio: 1/1)')
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches

// H.264 MP4 plays almost everywhere; VP9 WebM covers browsers without H.264
// (Firefox on Windows N, some Linux builds). Pick the one the browser says it
// can play, and fall back to the other if it fails anyway.
function videoSources(shape) {
  const mp4 = `${VIDEO}${shape}.mp4`
  const webm = `${VIDEO}${shape}.webm`
  const probe = document.createElement('video')
  const h264 = probe.canPlayType('video/mp4; codecs="avc1.640028"')
  const vp9 = probe.canPlayType('video/webm; codecs="vp9"')
  return !h264 && vp9 ? [webm, mp4] : [mp4, webm]
}
// ?debug shows why the intro skipped to the page, and the screen measurements
const debug = new URLSearchParams(location.search).has('debug')
// ?autoplay=blocked or ?autoplay=hang acts like a browser that refuses or
// ignores autoplay (Opera, Brave...), to test the automatic fallback anywhere
const requestedAutoplayTest = new URLSearchParams(location.search).get('autoplay')
const autoplayTest = debug && ['blocked', 'hang'].includes(requestedAutoplayTest)
  ? requestedAutoplayTest : null

// Keep the rejection context after the video is removed. The error name alone
// cannot distinguish browser settings, an embedding policy, or a test failure.
function playbackDiagnostics(v, error) {
  const read = (get) => {
    try { return get() ?? 'unknown' } catch { return 'unavailable' }
  }
  const policy = document.permissionsPolicy || document.featurePolicy
  return [
    'autoplay audit v1',
    `message: ${error.message || '(none)'}`,
    `test: ${autoplayTest || 'off'}; embedded: ${window.top !== window.self}`,
    `muted: ${v.muted}; defaultMuted: ${v.defaultMuted}; volume: ${v.volume}`,
    `autoplay policy: ${read(() => navigator.getAutoplayPolicy?.(v))}`,
    `document allows autoplay: ${read(() => policy?.allowsFeature('autoplay'))}`,
    `visibility: ${document.visibilityState}; active: ${read(() => navigator.userActivation?.isActive)}`,
    `source: ${(v.currentSrc || v.src).split('/').pop()}`,
    `ready: ${v.readyState}; network: ${v.networkState}; time: ${v.currentTime}`,
    `media error: ${v.error?.code ?? 'none'} ${v.error?.message || ''}`,
  ].join('\n')
}

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
  const [sources] = useState(() => videoSources(videoOrientation))
  const [landed, setLanded] = useState(false)
  const [videoDone, setVideoDone] = useState(false)
  const [why, setWhy] = useState('starting')
  const video = useRef(null)
  const stage = useRef(null)

  const finish = (reason) => {
    setWhy(reason)
    setLanded(true)
    setVideoDone(true)
  }

  // play, and hand over to the page when the camera lands
  useEffect(() => {
    const v = video.current
    if (!v) return
    let frame
    let disposed = false
    let source = 0
    let previousTime = v.currentTime
    let lastTick = performance.now()
    let idleFor = 0         // visible time without playback advancing
    const watch = () => {
      if (disposed) return
      if (v.currentTime >= LAND_AT) setLanded(true)
      frame = requestAnimationFrame(watch)
    }
    // phones only autoplay video that is muted as an attribute, not just a property
    v.muted = v.defaultMuted = true
    v.setAttribute('muted', '')
    const play = () => {
      idleFor = 0
      lastTick = performance.now()
      const request = autoplayTest
        ? (autoplayTest === 'hang' ? new Promise(() => {})
          : Promise.reject(new DOMException('test', 'NotAllowedError')))
        : v.play()
      request.then(() => {
        if (disposed) return
        setWhy('playing')
      }, (e) => {
        // AbortError only means a newer load()/play() replaced this one
        if (!disposed && e.name !== 'AbortError') {
          finish(`play() refused: ${e.name}${debug ? `\n${playbackDiagnostics(v, e)}` : ''}`)
        }
      })
    }
    const failed = () => {
      if (source + 1 < sources.length) {
        source += 1
        setWhy(`video error ${v.error?.code}, trying ${sources[source].split('/').pop()}`)
        v.src = sources[source]
        v.load()
        play()
      } else {
        finish(`video error ${v.error?.code} (${videoOrientation})`)
      }
    }
    const visibilityChanged = () => {
      lastTick = performance.now()
      idleFor = 0
      if (!document.hidden && v.paused && !v.ended) play()
    }
    v.addEventListener('error', failed)
    // backup for watch(): animation frames pause in background tabs
    const timeUpdate = () => v.currentTime >= LAND_AT && setLanded(true)
    v.addEventListener('timeupdate', timeUpdate)
    document.addEventListener('visibilitychange', visibilityChanged)
    if (!document.hidden) play()
    watch()
    const watchdog = setInterval(() => {
      const now = performance.now()
      if (!document.hidden && v.currentTime === previousTime && !v.ended) {
        idleFor += now - lastTick
      } else {
        idleFor = 0
      }
      previousTime = v.currentTime
      lastTick = now
      // paused and going nowhere: autoplay was blocked without saying so
      if (v.paused && idleFor >= START_MS) finish(`not started after ${START_MS / 1000}s`)
      else if (idleFor >= STALL_MS) {
        finish(`stalled ${STALL_MS / 1000}s (readyState ${v.readyState}, networkState ${v.networkState})`)
      }
    }, 250)
    return () => {
      disposed = true
      cancelAnimationFrame(frame)
      clearInterval(watchdog)
      v.removeEventListener('error', failed)
      v.removeEventListener('timeupdate', timeUpdate)
      document.removeEventListener('visibilitychange', visibilityChanged)
    }
  }, [videoDone])

  // the page's only motion: the words and button appear once the screen is white
  useLayoutEffect(() => {
    if (!landed || reducedMotion) return
    const ctx = gsap.context(() => {
      gsap.from('.details', { opacity: 0, duration: 0.9, ease: 'power2.out' })
    }, stage)
    return () => ctx.revert()
  }, [landed])

  return (
    // while the video plays the stage keeps the video's shape (a resize or a
    // turned phone just crops it differently); afterwards it follows the screen
    <main className={`intro ${videoDone ? orientation : videoOrientation}`}>
      <div className="stage" ref={stage}>
        {/* sits exactly where the logo lands in the video, so the handover is invisible */}
        <h1 className="mark">
          <img src={`${BASE}exxy-logo.svg`} alt="EXXY" />
        </h1>

        {!videoDone && (
          <video
            ref={video}
            className="backdrop"
            src={sources[0]}
            poster={`${VIDEO}${videoOrientation}-start.jpg`}
            muted
            autoPlay={!autoplayTest}
            playsInline
            preload="auto"
            aria-hidden="true"
            onEnded={() => finish('video ended')}
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
