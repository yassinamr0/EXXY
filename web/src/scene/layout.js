// All measurements in metres. Three.js is Y-up; the camera starts at +Z
// (the entrance) and looks down the terrace towards -Z (the far wall).

export const TERRACE = {
  halfWidth: 3.5,
  height: 3.4,
  near: 10.5, // entrance edge of the floor
  far: -9, // inner face of the far wall
  opening: { width: 3.2, height: 2.7 }, // view to the sea in the far wall
}

// Low golden-hour sun from the left, slightly ahead of the visitor, so light
// falls between the left piers and rakes across the floor.
export const SUN = { position: [-10, 4.2, -6], color: '#ffc48a', intensity: 4.2 }

export const CAMERA = {
  start: [0, 1.5, 9.8],
  target: [0, 1.35, -9],
}

// Powder-coat colours from EXXY's own option lists.
export const SETS = [
  { table: [-1.85, 3.2], tableColor: '#ece8e1', chairColor: '#d9ccb4' },
  { table: [1.85, -2.6], tableColor: '#3d4043', chairColor: '#6f7a58' },
]
