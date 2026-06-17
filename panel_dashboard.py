from __future__ import annotations

from pathlib import Path
import json

import panel as pn
import param

pn.extension(sizing_mode="stretch_width")

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "plot_manifest.json"


class StaticMapDashboard(pn.custom.JSComponent):
    """Static Panel dashboard that swaps pre-rendered Plotly HTML maps."""

    title = param.String(default="Map dashboard")
    groups = param.List(default=[])
    indicators = param.List(default=[])
    group_level = param.String(default="")
    indicator = param.String(default="")
    manifest = param.Dict(default={})

    _esm = r"""
    export function render({ model }) {
      const root = document.createElement('div');
      root.style.width = '100%';
      root.style.display = 'flex';
      root.style.flexDirection = 'column';
      root.style.gap = '1rem';

      const controls = document.createElement('div');
      controls.style.display = 'flex';
      controls.style.flexWrap = 'wrap';
      controls.style.gap = '1rem';
      controls.style.alignItems = 'end';

      function makeControl(labelText) {
        const wrap = document.createElement('div');
        wrap.style.minWidth = '220px';

        const label = document.createElement('label');
        label.textContent = labelText;
        label.style.display = 'block';
        label.style.fontWeight = '600';
        label.style.marginBottom = '0.35rem';

        const select = document.createElement('select');
        select.style.width = '100%';
        select.style.padding = '0.45rem 0.5rem';
        select.style.borderRadius = '8px';
        select.style.border = '1px solid #d1d5db';
        select.style.background = 'white';

        wrap.appendChild(label);
        wrap.appendChild(select);
        return { wrap, select };
      }

      function humanize(value) {
        return String(value).replaceAll('_', ' ');
      }

      function fillSelect(select, values, current) {
        select.innerHTML = '';
        values.forEach((value) => {
          const option = document.createElement('option');
          option.value = value;
          option.textContent = humanize(value);
          select.appendChild(option);
        });
        if (current && values.includes(current)) {
          select.value = current;
        } else if (values.length > 0) {
          select.value = values[0];
        }
      }

      const groupControl = makeControl('Group level');
      const indicatorControl = makeControl('Indicator');
      controls.appendChild(groupControl.wrap);
      controls.appendChild(indicatorControl.wrap);

      const mapFrame = document.createElement('iframe');
      mapFrame.id = 'mapFrame';
      mapFrame.style.width = '100%';
      mapFrame.style.height = '82vh';
      mapFrame.style.border = '0';
      mapFrame.style.borderRadius = '16px';
      mapFrame.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.08)';
      mapFrame.loading = 'lazy';

      function updateFrame() {
        const key = `${groupControl.select.value}::${indicatorControl.select.value}`;
        const src = model.manifest?.plots?.[key];
        mapFrame.src = src || 'about:blank';
        model.group_level = groupControl.select.value || '';
        model.indicator = indicatorControl.select.value || '';
      }

      fillSelect(groupControl.select, model.groups || [], model.group_level);
      fillSelect(indicatorControl.select, model.indicators || [], model.indicator);

      groupControl.select.addEventListener('change', updateFrame);
      indicatorControl.select.addEventListener('change', updateFrame);

      root.appendChild(controls);
      root.appendChild(mapFrame);
      updateFrame();
      return root;
    }
    """


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path.name}. Run scripts/build_manifest.py first."
        )
    return json.loads(path.read_text(encoding='utf-8'))


def make_dashboard(manifest: dict | None = None) -> pn.Column:
    manifest = manifest or load_manifest()
    groups = manifest.get('groups', [])
    indicators = manifest.get('indicators', [])

    dashboard = StaticMapDashboard(
        title='Map dashboard',
        groups=groups,
        indicators=indicators,
        group_level=groups[0] if groups else '',
        indicator=indicators[0] if indicators else '',
        manifest=manifest,
        height=900,
    )

    return pn.Column(
        pn.pane.Markdown(
            "# Map dashboard\n\nChoose a group level and an indicator to switch between the pre-rendered maps.",
            margin=(0, 0, 10, 0),
        ),
        dashboard,
        sizing_mode='stretch_width',
    )


if __name__ == '__main__':
    make_dashboard().servable()
