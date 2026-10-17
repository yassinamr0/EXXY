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
- Site: exxyshop.com, very likely Shopify (not yet confirmed — the site is blocked from the cloud environment).

## Decisions made
| # | Decision | Why |
|---|----------|-----|
| 1 | Intro scene is an **outdoor architectural terrace** (Mediterranean / North Coast feel), not an indoor room | EXXY sells outdoor furniture; it looks right in its natural setting |
| 2 | First deliverable is a **demo for a pitch**, not the production site | No admin access yet |
| 3 | Demo uses a **local product data file**, not a live Shopify connection | No access needed; structured so it can be swapped for Shopify later |
| 4 | Demo is shared through a **private, non-indexed link** | It uses EXXY's name, logo and photos without their approval yet |

## Open questions
- Is the 3D scene **only the intro**, or also a browsable showroom? (Deferred — intro first; build it so it can grow.)
- Which furniture photos are available, and from how many angles?
- Is there a deadline for the pitch?
- Budget for an AI image-to-3D tool (free credits only, or ~$20–30 for one month)?
- How do customers really order (online, WhatsApp/phone, projects)? Ask EXXY during the pitch.
- Confirm platform (Shopify?) once exxyshop.com is reachable.

## Proposed demo scope
1. **3D intro** — terrace, 3–5 real EXXY pieces, camera moves forward, logo + "Explore the collection" reveal. Skip button, short mobile version, still-image fallback.
2. **Home page below the intro** — brand statement, collections, featured products.
3. **Collection page + 3–4 product pages** — photos, materials, dimensions, finishes.
4. **Inquiry** — "Request a quote" and WhatsApp buttons (form can be non-functional in the demo).
5. **About** — the 1999 metalwork story.

## Phases
- [x] A. Initial look at the current site (via search; full inspection pending network access)
- [ ] B. Design direction for the terrace intro and site style
- [ ] C. 3D test: convert 2–3 products, compare with photos
- [ ] D. Demo site structure (above)
- [ ] E. Build: proof of concept (scene + camera) → demo pages → deploy private link

## Completed
- Repo created (empty).
- Public research on EXXY's site and products.
