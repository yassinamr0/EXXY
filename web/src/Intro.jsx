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
  // the video is picked once, for the screen shape at load
  const [videoOrientation] = useState(orientation)
  const [landed, setLanded] = useState(reducedMotion || saveData)
  const [videoDone, setVideoDone] = useState(reducedMotion || saveData)
  const video = useRef(null)
  const stage = useRef(null)

  const finish = () => {
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
    v.play().then(watch, finish)
    const stall = setTimeout(() => v.currentTime < 0.1 && finish(), STALL_MS)
    v.addEventListener('error', finish)
    return () => {
      cancelAnimationFrame(frame)
      clearTimeout(stall)
      v.removeEventListener('error', finish)
    }
  }, [])

  // turning the phone mid-intro skips to the page, laid out for the new shape
  useEffect(() => {
    if (orientation !== videoOrientation) finish()
  }, [orientation, videoOrientation])

  // the page's only motion: the words and button appear once the screen is white
  useLayoutEffect(() => {
    if (!landed || reducedMotion) return
    const ctx = gsap.context(() => {
      gsap.from('.details', { opacity: 0, duration: 0.9, ease: 'power2.out' })
    }, stage)
    return () => ctx.revert()
  }, [landed])

  const skip = () => {
    video.current?.pause()
    finish()
  }

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

      {!landed && (
        <button type="button" className="skip" onClick={skip}>
          Skip intro
        </button>
      )}
    </main>
  )
}
