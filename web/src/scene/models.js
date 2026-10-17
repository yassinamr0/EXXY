import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import tableData from '../models/ex_dt_01.glb?inline'
import chairData from '../models/lines.glb?inline'

// The models are embedded in the page as base64 and parsed directly,
// so loading them never needs a network request (the preview host blocks
// those, and it saves a round trip on slow mobile connections).
function parse(dataUrl) {
  const bytes = Uint8Array.from(atob(dataUrl.split(',')[1]), (c) => c.charCodeAt(0))
  return new Promise((resolve, reject) => new GLTFLoader().parse(bytes.buffer, '', resolve, reject))
}

export const models = {
  table: parse(tableData),
  chair: parse(chairData),
}
