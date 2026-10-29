# Reviewer preview

The GitHub Pages build sets `VITE_REVIEWER_DEMO=true` and embeds the deterministic fictional fixture dataset in the frontend. It makes no API request and requires no backend, secrets, database, or collector. The interface prominently identifies the source as DEMO and explains that no network is being monitored.

The main branch workflow builds `frontend/` with the repository subpath and deploys the output through GitHub Pages. The public URL is https://trusegone.github.io/SEGONE-NETWATCH/ once the first Pages deployment completes. The repository must have Pages configured to use GitHub Actions. If Actions reports Pages is disabled, select **Settings → Pages → Build and deployment → Source: GitHub Actions**, then rerun the workflow.
