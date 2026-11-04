# DESIGN.md — Stats Desk

## Brief

Hiring managers and recruiters open this page to answer one question in under 30 seconds: is Joe worth an interview for a data analyst / scientist / engineer role?

**Job of the page:** name + role + location in the hero; background holds the “what he builds” line + collaboration line; 5 impact-first projects with real thumbs; resume + contact. No product-marketing theater.

**Signature move:** left-aligned "stats desk" — paper surface, ink type, numbered project list, one navy accent. Typography and whitespace do the work.

## Locked fonts

| Role | Face | Why |
| --- | --- | --- |
| Display / name | **IBM Plex Sans** (600/700) | Engineered grotesque; not Inter / Roboto / Space Grotesk / Bebas |
| Body | **IBM Plex Sans** (400/500) | Same family keeps the desk quiet |
| Labels / meta / numbers | **IBM Plex Mono** (400/500) | Desk / runbook signal without terminal cosplay |

Source: Google Fonts CDN (`IBM+Plex+Sans`, `IBM+Plex+Mono`). Do not swap without updating this file first.

## Tokens

Intent and boundary on every token. Use only these CSS variables in `index.html`.

| Token | Value | Intent | Boundary |
| --- | --- | --- | --- |
| `--paper` | `#f7f8f9` | Cool light desk surface | Not cream `#F4F1EA`; not warm parchment; not dark `#0a0a0a` default |
| `--ink` | `#121417` | Primary text | Near-black, not pure `#000` |
| `--ink-muted` | `#5c6570` | Secondary / meta | Must stay AA on `--paper` |
| `--line` | `#d8dde3` | Hairline rules | No soft colored gold lines |
| `--accent` | `#1e4d6b` | Links, focus, one CTA | Single accent; muted stadium navy from prior field; not gold shimmer; not purple/indigo |
| `--accent-hover` | `#163a52` | Hover/active for accent | Darker only |
| `--thumb-bg` | `#e8ecf0` | Thumbnail placeholder field | Neutral; no gradient fills |
| `--radius` | `4px` | Soft corners on thumbs/photo only | Never `999px` / pills |
| `--shadow` | `none` | Flat desk | No `shadow-lg`, no glow |
| `--measure` | `38rem` | Readable body width | Left-aligned; do not center body copy |
| `--space-1` … `--space-6` | `0.25 / 0.5 / 1 / 1.5 / 2.5 / 4 rem` | Rhythm | Prefer uneven section air over equal card grids |
| `--font-sans` | `"IBM Plex Sans", system-ui, sans-serif` | Locked | |
| `--font-mono` | `"IBM Plex Mono", ui-monospace, monospace` | Locked | |

## Layout rules

1. Left-aligned name, role, and body. Center nothing except the photo column on wide screens.
2. Projects are a **numbered vertical list** with thumbnail + title + one impact sentence + tools as plain mono text (not pill chips).
3. Nav is a short personal-site bar (About / Work / Contact / Resume). No Product/Company/Resources footer.
4. Skills: one compact mono line under About, not a tag cloud.
5. Contact: email / LinkedIn / GitHub as text links. No particle canvas, no emoji icon tiles.
6. Motion: at most two intentional moments (e.g. link underline, subtle project-row hover). Respect `prefers-reduced-motion`. Always style `:focus-visible`.

## Component decisions

- **Cards:** do not wrap projects in bordered/shadowed cards. Hairline separators only.
- **Buttons:** one solid accent resume button; secondary links are text.
- **Badges:** plain mono label next to title (e.g. `Founder`), not pills.
- **Images:** real headshot + project thumbs already in repo root. No stock people, no fake UI divs.

## Nevers

- Inter, Roboto, Arial, system-only stacks, Space Grotesk, Bebas Neue, DM Sans as the identity pair
- Purple / indigo gradients; cream `#F4F1EA` + terracotta `#D97757` package; gold shimmer accents
- Dark mode as the default theme
- Glass / blur nav, glow, aurora blobs, gradient text, noise overlays as decoration
- Centered SaaS hero with dual CTAs or "Introducing" pills
- Three equal icon feature cards / bento cardocalypse / skill-tag pill clusters
- Rounded-full pills; multi-layer shadows; emoji-as-icons; sparkles for AI/ML
- Broadsheet dense newspaper columns; sticky SaaS 4-column footers
- Generic copy: unlock, seamless, elevate, crafting elegant solutions, data-driven decisions (alone)
- Decorative canvas / particle networks; fade-up-on-scroll on every block
- Invented testimonials, stock imagery, fake logos

## Content voice

Impact first, tools second. Domain-specific (sports analytics, pipelines, models). Sound like a person who ships, not a landing page.
