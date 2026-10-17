import { use, useMemo } from 'react'
import * as THREE from 'three'
import { models } from './models.js'
import { SETS } from './layout.js'

/** Copy of a loaded model, recoloured in one of EXXY's powder-coat colours. */
function Model({ name, color, ...props }) {
  const { scene } = use(models[name])
  const object = useMemo(() => {
    const copy = scene.clone(true)
    copy.traverse((o) => {
      if (!o.isMesh) return
      o.material = o.material.clone()
      o.material.color = new THREE.Color(color)
      o.castShadow = o.receiveShadow = true
    })
    return copy
  }, [scene, color])
  return <primitive object={object} {...props} />
}

/**
 * Dining set: EX-DT-01 table with its long side along the terrace,
 * two LINES chairs on each side facing it.
 */
function DiningSet({ table: [x, z], tableColor, chairColor }) {
  const chairs = []
  for (const side of [-1, 1]) {
    for (const dz of [-0.45, 0.45]) {
      chairs.push({
        position: [x + side * 0.72, 0, z + dz],
        // models face +Z; turn each chair towards the table
        rotation: [0, side * -Math.PI / 2, 0],
      })
    }
  }
  return (
    <group>
      <Model name="table" color={tableColor} position={[x, 0, z]} rotation-y={Math.PI / 2} />
      {chairs.map((c, i) => <Model key={i} name="chair" color={chairColor} {...c} />)}
    </group>
  )
}

export default function Furniture() {
  return SETS.map((set, i) => <DiningSet key={i} {...set} />)
}
