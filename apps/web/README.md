# apps/web

Browser application for reading and exploring Paper IR.

The web app does not own paper analysis content. It fetches Paper IR from the API and renders:

- overview,
- structure graph,
- formula cards,
- claim-evidence chains,
- method deltas,
- experiment matrix,
- reproduction roadmap,
- source anchor panel.

Current implementation is a static web app under `static/`, served locally by:

```bash
npm run dev
```
