# Deploy the dashboard gallery to Vercel

The Power BI report itself can't run on the web, and **Streamlit can't run on Vercel**
(Vercel is serverless; Streamlit needs a persistent server). So for Vercel we ship a
**static site** that mirrors the dashboard gallery.

> ✅ Nothing else in the repo is removed — `app.py` (Streamlit), the PBIX, the cleaning
> script and data all stay. Vercel only deploys the `public/` folder.

## What powers the Vercel deploy
```
public/
├── index.html        ← the static gallery (self-contained HTML + CSS)
└── img/              ← web-safe copies of the dashboard screenshots
vercel.json           ← tells Vercel: no build, serve public/ as static
.vercelignore         ← keeps the PBIX / data / Python out of the upload
```

`vercel.json` sets `outputDirectory: public` with no build step, so Vercel just serves the
static files — no Python, no install, instant deploy.

---

## Option A — Deploy from the Vercel website (easiest)
1. Push this repo to GitHub (already done).
2. Go to **https://vercel.com/new** and sign in with GitHub.
3. **Import** the `POWERBI_Youtube_Dashboard` repo.
4. Vercel reads `vercel.json` automatically — leave all build settings empty/default.
5. Click **Deploy**. In ~20s you get a live URL like
   `https://powerbi-youtube-dashboard.vercel.app`.
6. Every future `git push` to `main` auto-redeploys.

## Option B — Deploy from the command line
```bash
npm i -g vercel          # one-time
cd POWERBI_Youtube_Dashboard
vercel                   # first run: links the project, deploys a preview
vercel --prod            # promote to your production URL
```

---

## Updating the site
- **New screenshots?** Re-export the pages, copy them into `public/img/` using the same
  web-safe names (`overview.png`, `country-comparison.png`, `category-content.png`,
  `channels-top-videos.png`, `timing-virality.png`), commit, and push.
- **Text/layout changes?** Edit `public/index.html` and push.

## Test it locally first
```bash
cd public
python -m http.server 8777
# open http://localhost:8777
```

## Notes
- The static site is a **gallery/preview** — slicers, tooltips and drill-through are described
  but not interactive (that's the live Power BI report). For an interactive Python version,
  host `app.py` on Streamlit Community Cloud instead.
- The `.vercelignore` ensures the 152 MB LFS-tracked PBIX is never uploaded to Vercel.
