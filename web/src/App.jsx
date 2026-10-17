import { Suspense, useEffect, useRef } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'
import Terrace from './scene/Terrace.jsx'
import Furniture from './scene/Furniture.jsx'
import { CAMERA, SUN } from './scene/layout.js'

const isMobile = matchMedia('(pointer: coarse)').matches
const debugOrbit = new URLSearchParams(location.search).has('orbit')

/**
 * Keeps the framing right on every screen: holds roughly a 62° horizontal
 * view on wide screens, and caps the vertical angle on tall phones so the
 * picture doesn't distort.
 */
function ResponsiveCamera() {
  const { camera, size } = useThree()
  useEffect(() => {
    const aspect = size.width / size.height
    const hfov = THREE.MathUtils.degToRad(62)
    const vfov = 2 * Math.atan(Math.tan(hfov / 2) / aspect)
    camera.fov = THREE.MathUtils.clamp(THREE.MathUtils.radToDeg(vfov), 38, 72)
    camera.position.set(...CAMERA.start)
    camera.lookAt(...CAMERA.target)
    camera.updateProjectionMatrix()
  }, [camera, size])
  return null
}

function Sun() {
  const light = useRef()
  useEffect(() => {
    // the light aims at the middle of the terrace
    light.current.target.position.set(0, 0, 0)
    light.current.target.updateMatrixWorld()
  }, [])
  const s = 13
  return (
    <directionalLight
      ref={light}
      position={SUN.position}
      color={SUN.color}
      intensity={SUN.intensity}
      castShadow
      shadow-mapSize={isMobile ? [1024, 1024] : [2048, 2048]}
      shadow-bias={-0.0004}
      shadow-normalBias={0.02}
      shadow-camera-left={-s}
      shadow-camera-right={s}
      shadow-camera-top={s}
      shadow-camera-bottom={-s}
      shadow-camera-near={1}
      shadow-camera-far={40}
    />
  )
}

/** Frames-per-second readout for testing on real phones. */
function Fps({ target }) {
  const frames = useRef(0)
  const last = useRef(performance.now())
  useFrame(() => {
    frames.current++
    const now = performance.now()
    if (now - last.current >= 1000) {
      if (target.current) target.current.textContent = `${frames.current} fps`
      frames.current = 0
      last.current = now
    }
  })
  return null
}

export default function App() {
  const fpsEl = useRef()
  return (
    <>
      <Canvas
        shadows="soft"
        dpr={[1, isMobile ? 1.5 : 2]}
        camera={{ near: 0.1, far: 1000 }}
        gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.15 }}
      >
        <ResponsiveCamera />
        <hemisphereLight args={['#c9d6e2', '#e8c49a', 1.5]} />
        <Sun />
        <fog attach="fog" args={['#f1d9bb', 30, 160]} />
        <Suspense fallback={null}>
          <Terrace />
          <Furniture />
        </Suspense>
        {debugOrbit && <OrbitControls target={[0, 1, 0]} />}
        <Fps target={fpsEl} />
      </Canvas>
      <div className="fps" ref={fpsEl} aria-hidden="true">– fps</div>
    </>
  )
}
