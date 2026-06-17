# Static Quarto + Panel map dashboard

This project is set up for GitHub Pages.

## File naming convention

Put your pre-rendered Plotly map HTML files into `plots/` using this pattern:

```text
<group_level>__<indicator>.html
```

Examples:

```text
plots/district__poverty.html
plots/region__income.html
plots/country__deprivation.html
```

## Build

Run:

```bash
python build_site.py
```

That script will:

1. scan `plots/` and create `plot_manifest.json`
2. export the static Panel dashboard to `_build/panel-dashboard.html`
3. render the Quarto site to `docs/`
4. copy the Panel export and plot HTML files into `docs/`

## Publish to GitHub Pages

In your repository settings, set GitHub Pages to serve from the `docs/` folder on the branch you push.

## Notes

- The Panel dashboard is static because it only swaps between pre-rendered HTML files.
- The dropdown behavior is implemented in JavaScript, so it works on GitHub Pages without a Python server.
