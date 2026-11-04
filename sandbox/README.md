# Sandbox preview

Mess around here before production. Do not push design experiments to `main` until you explicitly approve a promote.

## Branch

Work on the `sandbox` branch. Production GitHub Pages publishes from `main`.

## Local preview

From the repo root (`joe-digiovanni-portfolio-site`):

```bash
npm run serve
```

Open [http://localhost:3456](http://localhost:3456).

Equivalent: `python3 -m http.server 3456`.

Keep `index.html` and asset siblings (`*.pdf`, `*.jpg`, `*.png`) in the repo root so relative paths match GitHub Pages.

## Promote to production

Only when you say so: merge `sandbox` into `main` and push `origin/main`. That updates [jdigiovanni4.github.io/joe-digiovanni-portfolio](https://jdigiovanni4.github.io/joe-digiovanni-portfolio/).
