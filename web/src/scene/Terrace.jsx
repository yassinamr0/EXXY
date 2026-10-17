import { useLayoutEffect, useMemo, useRef } from 'react'
import * as THREE from 'three'
import { TERRACE, SUN } from './layout.js'
import { travertineTexture, plasterTexture } from './textures.js'

const { halfWidth: HW, height: H, near: NEAR, far: FAR, opening } = TERRACE
const LENGTH = NEAR - FAR
const BALCONY = 2.5

function Box({ position, size, material }) {
  return (
    <mesh position={position} material={material} castShadow receiveShadow>
      <boxGeometry args={size} />
    </mesh>
  )
}

/** Thin slats overhead; one draw call for all of them. */
function Pergola({ material }) {
  const ref = useRef()
  const slats = useMemo(() => {
    const zs = []
    for (let z = NEAR - 1.5; z > FAR + 0.3; z -= 0.7) zs.push(z)
    return zs
  }, [])
  useLayoutEffect(() => {
    const m = new THREE.Matrix4()
    slats.forEach((z, i) => ref.current.setMatrixAt(i, m.makeTranslation(0, H + 0.07, z)))
    ref.current.instanceMatrix.needsUpdate = true
  }, [slats])
  return (
    <instancedMesh ref={ref} args={[null, material, slats.length]} castShadow>
      <boxGeometry args={[HW * 2 + 0.6, 0.1, 0.05]} />
    </instancedMesh>
  )
}

/** Gradient sky with a warm glow towards the sun. */
function Sky() {
  const material = useMemo(() => new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      sunDir: { value: new THREE.Vector3(...SUN.position).normalize() },
    },
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 sunDir;
      varying vec3 vDir;
      void main() {
        float h = clamp(vDir.y, 0.0, 1.0);
        vec3 horizon = vec3(0.98, 0.80, 0.60);
        vec3 zenith = vec3(0.55, 0.69, 0.80);
        vec3 col = mix(horizon, zenith, pow(h, 0.55));
        float glow = pow(max(dot(vDir, sunDir), 0.0), 8.0);
        col += vec3(1.0, 0.62, 0.30) * glow * 0.45;
        gl_FragColor = vec4(col, 1.0);
        #include <colorspace_fragment>
      }`,
  }), [])
  return (
    <mesh material={material} renderOrder={-1}>
      <sphereGeometry args={[400, 32, 16]} />
    </mesh>
  )
}

export default function Terrace() {
  const mats = useMemo(() => {
    const floorMap = travertineTexture()
    floorMap.repeat.set((HW * 2 + 6) / 2.4, (LENGTH + BALCONY) / 2.4)
    const plasterMap = plasterTexture()
    plasterMap.repeat.set(4, 2)
    return {
      floor: new THREE.MeshStandardMaterial({ map: floorMap, roughness: 0.8 }),
      plaster: new THREE.MeshStandardMaterial({ map: plasterMap, roughness: 0.95 }),
      timber: new THREE.MeshStandardMaterial({ color: '#f3ebdf', roughness: 0.9 }),
      sea: new THREE.MeshStandardMaterial({ color: '#87a4b4', roughness: 0.35, fog: false }),
    }
  }, [])

  // piers along the left side let the low sun through in bands
  const piers = []
  for (let z = NEAR - 1.2; z > FAR; z -= 2.6) piers.push(z)

  const sideW = (HW * 2 - opening.width) / 2
  return (
    <group>
      <Sky />

      {/* floor (runs past the far wall onto a narrow balcony) */}
      <mesh rotation-x={-Math.PI / 2} position={[0, 0, (NEAR + FAR - BALCONY) / 2]}
        material={mats.floor} receiveShadow>
        <planeGeometry args={[HW * 2 + 6, LENGTH + BALCONY]} />
      </mesh>

      {/* left colonnade + beam */}
      {piers.map((z) => (
        <Box key={z} position={[-HW - 0.22, H / 2, z]} size={[0.45, H, 0.5]} material={mats.plaster} />
      ))}
      <Box position={[-HW - 0.22, H - 0.25, (NEAR + FAR) / 2]} size={[0.45, 0.5, LENGTH]} material={mats.plaster} />

      {/* right wall, solid: it catches the warm light */}
      <Box position={[HW + 0.15, H / 2, (NEAR + FAR) / 2]} size={[0.3, H, LENGTH]} material={mats.plaster} />

      {/* far wall with a framed opening to the sea */}
      <Box position={[-HW + sideW / 2, H / 2, FAR - 0.15]} size={[sideW, H, 0.3]} material={mats.plaster} />
      <Box position={[HW - sideW / 2, H / 2, FAR - 0.15]} size={[sideW, H, 0.3]} material={mats.plaster} />
      <Box position={[0, (H + opening.height) / 2, FAR - 0.15]}
        size={[opening.width, H - opening.height, 0.3]} material={mats.plaster} />

      <Pergola material={mats.timber} />

      {/* low balcony wall, kept below eye level so the sea shows */}
      <Box position={[0, 0.2, FAR - BALCONY + 0.12]} size={[HW * 2 + 6, 0.4, 0.25]} material={mats.plaster} />
      <mesh rotation-x={-Math.PI / 2} position={[0, -3, -200]} material={mats.sea}>
        <planeGeometry args={[1200, 400]} />
      </mesh>
    </group>
  )
}
