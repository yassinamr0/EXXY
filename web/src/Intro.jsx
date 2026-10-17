import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import gsap from 'gsap'
import './intro.css'

const BASE = `${import.meta.env.BASE_URL}intro/`
const SHOP_URL = 'https://exxyshop.com/collections/all'

// The camera lands at 2.6 s (blender/terrace.py GLIDE_LAND); start the reveal
// a beat before so the name settles as the camera stops.
const REVEAL_AT = 2.45
// If the video hasn't started by then (slow network, Low Power Mode), show the
// landed view instead of a frozen first frame.
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
  const [stillOnly, setStillOnly] = useState(reducedMotion || saveData)
  const video = useRef(null)
  const overlay = useRef(null)

  // play, and land when the camera does (or straight away if playback fails)
  useEffect(() => {
    const v = video.current
    if (!v || stillOnly) return
    let frame
    const watch = () => {
      if (v.currentTime >= REVEAL_AT) return setLanded(true)
      frame = requestAnimationFrame(watch)
    }
    const fail = () => {
      setStillOnly(true)
      setLanded(true)
    }
    v.play().then(watch, fail)
    const stall = setTimeout(() => v.currentTime < 0.1 && fail(), STALL_MS)
    v.addEventListener('error', fail)
    return () => {
      cancelAnimationFrame(frame)
      clearTimeout(stall)
      v.removeEventListener('error', fail)
    }
  }, [stillOnly])

  // turning the phone mid-intro swaps to the landed picture for the new shape
  useEffect(() => {
    if (orientation !== videoOrientation) setLanded(true)
  }, [orientation, videoOrientation])

  // the one orchestrated moment: the name tightens into place as the camera brakes
  useLayoutEffect(() => {
    if (!landed) return
    const ctx = gsap.context(() => {
      if (reducedMotion) return
      gsap.timeline()
        .from('.wordmark', { '--track': '0.9em', opacity: 0, duration: 1.3, ease: 'expo.out' })
        .from('.floor', { opacity: 0, duration: 0.8, ease: 'power2.out' }, 0.45)
    }, overlay)
    return () => ctx.revert()
  }, [landed])

  const skip = () => {
    video.current?.pause()
    setStillOnly(true)
    setLanded(true)
  }

  // after a rotation, or when there is no video, show the landed frame as a picture
  const showVideo = !stillOnly && orientation === videoOrientation

  return (
    <main className={`intro ${orientation}`}>
      <div className="stage" ref={overlay}>
        {showVideo ? (
          <video
            ref={video}
            className="backdrop"
            src={`${BASE}${videoOrientation}.mp4`}
            poster={`${BASE}${videoOrientation}-start.jpg`}
            muted
            playsInline
            preload="auto"
            aria-hidden="true"
            onEnded={() => setLanded(true)}
          />
        ) : (
          <img className="backdrop" src={`${BASE}${orientation}-end.jpg`} alt="" />
        )}

        {landed && (
          <>
            <h1 className="wordmark">EXXY</h1>
            <div className="floor">
              <p className="tagline">Outdoor furniture, made in Egypt since 1999.</p>
              <a className="enter" href={SHOP_URL}>Explore the collection</a>
            </div>
          </>
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
