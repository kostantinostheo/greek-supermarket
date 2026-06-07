# Documentation

This website is built using [Docusaurus](https://docusaurus.io/) and deployed automatically to GitHub Pages.

**Live docs:** [https://kostantinostheo.github.io/greek-supermarket/](https://kostantinostheo.github.io/greek-supermarket/)

## Local Development

```bash
npm install
npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
npm run build
```

This command generates static content into the `build` directory.

## Deployment

Deployment is automated via GitHub Actions. Any push to `main` that changes files in the `docs/` directory triggers a build and deploy to GitHub Pages.
