# EXXY Website Redesign — Project Plan

## Goal right now
Build a **pitch demo** to show EXXY before we have admin access or full details.
The demo should prove the idea: a cinematic 3D intro using their real furniture,
followed by a clean, premium site experience.

## What we know about EXXY (from public search results)
- Egyptian **outdoor furniture** manufacturer; metal workshop since 1999.
- Categories: Chairs, Lounge Sets, Sunbeds & Loungers, Tables.
- Products are mostly aluminium / metal with powder coating, named by code (e.g. EX-DT-01, EX-TA-05).
- Prices in EGP; several items sold out, some listed at LE 0.00.
- Site: exxyshop.com — **confirmed Shopify** (default Dawn theme). 34 products, all priced LE 0.00 → sales happen by inquiry.
- Real projects are **hospitality** (cafés/restaurants). Full audit: `docs/site-audit.md`.

## Decisions made
| # | Decision | Why |
|---|----------|-----|
| 1 | Intro scene is an **outdoor architectural terrace** (Mediterranean / North Coast feel), not an indoor room | EXXY sells outdoor furniture; it looks right in its natural setting |
| 2 | First deliverable is a **demo for a pitch**, not the production site | No admin access yet |
| 3 | Demo uses a **local product data file**, not a live Shopify connection | No access needed; structured so it can be swapped for Shopify later |
| 4 | Demo is shared through a **private, non-indexed link** | It uses EXXY's name, logo and photos without their approval yet |
| 5 | Demo = **the 3D intro only** (no catalogue/product pages yet) | Show the idea first, gather feedback, then plan the rest |
| 6 | **$0 budget**: no paid tools or subscriptions | Use Claude Code, ChatGPT, Blender (free) and free AI 3D demos |
| 7 | **Mobile-first**: portrait phone is the main target, desktop must also look great | Most viewers will be on phones |
| 8 | Furniture modelled mainly by **Claude Code writing Blender Python scripts** from photos + listed dimensions; free AI image-to-3D only for comparison / cushions | EXXY's pieces are simple metal frames — scripted models are accurate, light and free |
| 9 | Tech for the demo: **Vite + React Three Fiber + GSAP** (no Next.js yet) | One page doesn't need Next.js; components move over later |
| 10 | Lighting: **golden hour** — low warm sun, long soft shadows, warm-glowing white walls | Most cinematic and premium |
| 11 | Project skills installed in `.claude/skills/`: find-skills, frontend-design, gsap-core/timeline/performance, web-design-guidelines | Official sources; saved in the repo so every session has them |

## Open questions
- Is the 3D scene **only the intro**, or also a browsable showroom? (Deferred — intro first; build it so it can grow.)
- Photos: only the public site photos (downloaded and reviewed).
- Many product photos look like European brand catalogue shots — ask EXXY about their own production photos.
- EXXY has no image logo — demo uses a placeholder wordmark (Instagram skipped).
- Which 3–5 pieces go in the scene? (Proposal: EX-DT-01, LINES, EX-TA-05, Panama Sunbed.)
- No deadline.
- How do customers really order (online, WhatsApp/phone, projects)? Ask EXXY during the pitch.
- Confirm platform (Shopify?) once exxyshop.com is reachable.

## Demo scope (intro only)
- Outdoor terrace, 3–5 real EXXY pieces along a central path.
- Camera glides forward (~4–6 s desktop, shorter on mobile), EXXY logo + button revealed at the far end.
- Skip button, reduced-motion support, still-image fallback for weak devices.

## Mobile performance rules
- Compose the shot for **portrait first**, then adapt for landscape/desktop.
- **Bake lighting and shadows in Blender** into textures (realistic look, almost free at runtime).
- Total download target **under ~5 MB**; compressed meshes (meshopt/Draco) and textures (KTX2/WebP).
- No real-time shadows or heavy post-processing on phones; cap pixel ratio.
- Show a poster image instantly while the 3D loads.
- Test on a real phone at every milestone.

## Phases
- [x] A. Site audit (`docs/site-audit.md`)
- [ ] B. Design direction for the terrace intro and site style
- [x] C. 3D test: EX-DT-01 table + LINES chair scripted in Blender (`blender/`), 26 KB + 63 KB GLB — close match to photos (`docs/3d-test/`)
- [ ] D. Demo site structure (above)
- [ ] E. Build: proof of concept (scene + camera) → demo pages → deploy private link

## Completed
- Repo created (empty).
- Public research on EXXY's site and products.
- Full site audit: platform, catalogue, projects, photos.
- Blender scripting pipeline (`blender/build.py`) + first two models in `assets/models/`.
