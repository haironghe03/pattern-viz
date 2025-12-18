#!/usr/bin/env python3
from pathlib import Path
import html

PROJECT_ROOT = Path(__file__).resolve().parent
CHINESE_DIR = PROJECT_ROOT / "Chinese"
# Base folder containing 4 sections, each with layercam/scorecam subfolders
BASE_DIR = PROJECT_ROOT / "12.17_ResNet50"
SECTIONS = [
    "nopretrain_singlecrop",
    "nopretrain_multicrop",
    "pretrain_singlecrop",
    "pretrain_multicrop",
]
OUTPUT_HTML = PROJECT_ROOT / "index_resnet50.html"

ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def list_images(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted([
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTS and not p.name.startswith("._")
    ])


def pick_single_image(dir_path: Path, base: str, method: str) -> str | None:
    """
    Choose a single representative image for the given method.
    Preference order: *_<method>_cam.jpg, *_<method>_cam_gb.jpg, *_<method>_gb.jpg
    """
    if not dir_path.exists():
        return None
    roots = [
        f"{base}_{method}_cam",
        f"{base}_{method}_cam_gb",
        f"{base}_{method}_gb",
    ]
    for root in roots:
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            candidate = dir_path / f"{root}{ext}"
            if candidate.exists():
                return candidate.relative_to(PROJECT_ROOT).as_posix()
    return None


def build_rows():
    chinese_images = list_images(CHINESE_DIR)
    rows = []
    for src in chinese_images:
        base = src.stem  # e.g., Chinese_B_0044
        chinese_rel = src.relative_to(PROJECT_ROOT).as_posix()

        section_images: list[tuple[str, str | None, str | None]] = []
        for section in SECTIONS:
            # Paths like: BASE_DIR/section/layercam/<base>/<files>
            layer_dir = BASE_DIR / section / "layercam" / base
            score_dir = BASE_DIR / section / "scorecam" / base
            layer_img = pick_single_image(layer_dir, base, "layercam")
            score_img = pick_single_image(score_dir, base, "scorecam")
            section_images.append((section, layer_img, score_img))

        rows.append({
            "base": base,
            "chinese": chinese_rel,
            "sections": section_images,
        })
    return rows


def render_html(rows: list[dict]) -> str:
    # Table: [Chinese] then for each section: [LayerCAM] [ScoreCAM]
    css = """
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 16px; }
    h1 { font-size: 20px; margin: 0 0 12px; }
    .meta { color: #666; font-size: 12px; margin-bottom: 16px; }
    table { border-collapse: collapse; width: 100%; table-layout: fixed; }
    thead th { position: sticky; top: 0; background: #fafafa; z-index: 1; }
    th, td { border: 1px solid #e5e5e5; vertical-align: top; padding: 6px; }
    td:first-child, th:first-child { width: 220px; }
    img.thumb { max-width: 100%; height: auto; display: block; }
    .row-title { font-weight: 600; font-size: 12px; color: #333; margin-bottom: 6px; word-break: break-all; min-height: 1em; }
    .section-label { font-size: 11px; color: #555; margin-bottom: 4px; }
    """

    head = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Pattern Viz Grid (ResNet50)</title>
  <style>{css}</style>
</head>
<body>
  <h1>Pattern Viz Grid (ResNet50)</h1>
  <div class=\"meta\">Source column: Chinese image. Then 4 sections (nopretrain_singlecrop, nopretrain_multicrop, pretrain_singlecrop, pretrain_multicrop), each with two columns: LayerCAM and ScoreCAM. Total rows: {len(rows)}</div>
  <table>
    <thead>
      <tr>
        <th>Source (Chinese)</th>
        {''.join(f'<th colspan=\"2\">{html.escape(section)}</th>' for section in [s for s, _, _ in rows[0]['sections']] ) if rows else ''}
      </tr>
      <tr>
        <th></th>
        {''.join('<th>LayerCAM</th><th>ScoreCAM</th>' for _ in ([s for s, _, _ in rows[0]['sections']] if rows else []))}
      </tr>
    </thead>
    <tbody>
"""

    body_parts = []
    for row in rows:
        base = html.escape(row["base"])
        chinese_img = row["chinese"]
        sections = row["sections"]

        cells = []
        src_cell = f'''
          <td>
            <div class=\"row-title\">{base}</div>
            <img class=\"thumb\" src=\"{html.escape(chinese_img)}\" alt=\"{base}\">
          </td>
        '''
        cells.append(src_cell)

        for section, layer_img, score_img in sections:
            if layer_img:
                cells.append(f'<td><img class=\"thumb\" src=\"{html.escape(layer_img)}\" alt=\"{base} {html.escape(section)} LayerCAM\"></td>')
            else:
                cells.append('<td></td>')
            if score_img:
                cells.append(f'<td><img class=\"thumb\" src=\"{html.escape(score_img)}\" alt=\"{base} {html.escape(section)} ScoreCAM\"></td>')
            else:
                cells.append('<td></td>')

        row_html = "<tr>\n" + "\n".join(cells) + "\n</tr>"
        body_parts.append(row_html)

    tail = """
    </tbody>
  </table>
</body>
</html>
"""
    return head + "\n".join(body_parts) + tail


def main():
    rows = build_rows()
    html_str = render_html(rows)
    OUTPUT_HTML.write_text(html_str, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
