import * as THREE from 'three'

// Small seeded random so the floor pattern is identical on every load.
function rng(seed) {
  return () => {
    seed = (seed * 16807) % 2147483647
    return (seed - 1) / 2147483646
  }
}

/**
 * Travertine paving drawn on a canvas: large 60 x 120 cm slabs laid in a
 * running bond, each slab slightly different in tone, with fine veins.
 * One texture tile covers 2.4 x 2.4 m (4 slabs across, 2 rows down).
 */
export function travertineTexture(size = 1024) {
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = size
  const ctx = canvas.getContext('2d')
  const rand = rng(7)
  const px = size / 2.4 // pixels per metre
  const joint = Math.max(1, Math.round(0.004 * px))

  ctx.fillStyle = '#d6c7b0'
  ctx.fillRect(0, 0, size, size)

  for (let row = 0; row < 2; row++) {
    const offset = row % 2 ? 0.3 : 0
    for (let col = -1; col < 5; col++) {
      const x = (col * 0.6 + offset) * px
      const y = row * 1.2 * px
      const w = 0.6 * px
      const h = 1.2 * px
      const l = 85 + rand() * 4
      ctx.fillStyle = `hsl(37 ${30 + rand() * 6}% ${l}%)`
      ctx.fillRect(x + joint, y + joint, w - joint * 2, h - joint * 2)

      // horizontal veins typical of vein-cut travertine
      ctx.save()
      ctx.beginPath()
      ctx.rect(x + joint, y + joint, w - joint * 2, h - joint * 2)
      ctx.clip()
      for (let v = 0; v < 26; v++) {
        const vy = y + rand() * h
        ctx.strokeStyle = `hsla(34, 32%, ${l - 6 - rand() * 8}%, ${0.06 + rand() * 0.12})`
        ctx.lineWidth = 0.5 + rand() * 2
        ctx.beginPath()
        ctx.moveTo(x, vy)
        ctx.bezierCurveTo(x + w * 0.3, vy + (rand() - 0.5) * 6,
          x + w * 0.7, vy + (rand() - 0.5) * 6, x + w, vy + (rand() - 0.5) * 4)
        ctx.stroke()
      }
      ctx.restore()
    }
  }

  const tex = new THREE.CanvasTexture(canvas)
  tex.colorSpace = THREE.SRGBColorSpace
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping
  tex.anisotropy = 8
  return tex
}

/** Very subtle mottling so lime-plaster walls don't look like flat CG. */
export function plasterTexture(size = 256) {
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = size
  const ctx = canvas.getContext('2d')
  const rand = rng(3)
  ctx.fillStyle = '#f6efe4'
  ctx.fillRect(0, 0, size, size)
  for (let i = 0; i < 900; i++) {
    const r = 4 + rand() * 18
    ctx.fillStyle = `hsla(34, 25%, ${88 + rand() * 8}%, 0.08)`
    ctx.beginPath()
    ctx.arc(rand() * size, rand() * size, r, 0, Math.PI * 2)
    ctx.fill()
  }
  const tex = new THREE.CanvasTexture(canvas)
  tex.colorSpace = THREE.SRGBColorSpace
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping
  return tex
}
