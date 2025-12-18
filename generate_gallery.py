#!/usr/bin/env python3
from pathlib import Path
import html

PROJECT_ROOT = Path(__file__).resolve().parent
CHINESE_DIR = PROJECT_ROOT / "Chinese"
LAYERCAM_DIR = PROJECT_ROOT / "layercam"
SCORECAM_DIR = PROJECT_ROOT / "scorecam"
HIRESCAM_DIR = PROJECT_ROOT / "hirescam"
OUTPUT_HTML = PROJECT_ROOT / "index.html"

ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def list_images(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted([
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTS and not p.name.startswith("._")
    ])


def list_dirs(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    return {p.name for p in directory.iterdir() if p.is_dir()}


def pick_method_images(dir_path: Path, base: str, method: str) -> list[str | None]:
    """
    Pick exactly three images for the given method in a fixed order:
    1) *_<method>_cam
    2) *_<method>_cam_gb
    3) *_<method>_gb
    If a target is missing, return None in that position.
    """
    if not dir_path.exists():
        return [None, None, None]
    roots = [
        f"{base}_{method}_cam",
        f"{base}_{method}_cam_gb",
        f"{base}_{method}_gb",
    ]
    results: list[str | None] = []
    for root in roots:
        chosen: str | None = None
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            candidate = dir_path / f"{root}{ext}"
            if candidate.exists():
                chosen = candidate.relative_to(PROJECT_ROOT).as_posix()
                break
        results.append(chosen)
    return results


def build_rows():
    chinese_images = list_images(CHINESE_DIR)
    layer_dirs = list_dirs(LAYERCAM_DIR)
    score_dirs = list_dirs(SCORECAM_DIR)
    hires_dirs = list_dirs(HIRESCAM_DIR)

    rows = []
    for src in chinese_images:
        base = src.stem  # e.g., Chinese_B_0044
        # Column 1: original image
        chinese_rel = src.relative_to(PROJECT_ROOT).as_posix()

        # Columns: LayerCAM (exactly 3 in fixed order)
        layer_imgs3: list[str | None] = [None, None, None]
        if base in layer_dirs:
            ldir = LAYERCAM_DIR / base
            layer_imgs3 = pick_method_images(ldir, base, "layercam")

        # Columns: ScoreCAM (exactly 3 in fixed order)
        score_imgs3: list[str | None] = [None, None, None]
        if base in score_dirs:
            sdir = SCORECAM_DIR / base
            score_imgs3 = pick_method_images(sdir, base, "scorecam")

        # Columns: HiresCAM (exactly 3 in fixed order)
        hires_imgs3: list[str | None] = [None, None, None]
        if base in hires_dirs:
            hdir = HIRESCAM_DIR / base
            hires_imgs3 = pick_method_images(hdir, base, "hirescam")

        rows.append({
            "base": base,
            "chinese": chinese_rel,
            "layercam3": layer_imgs3,
            "hirescam3": hires_imgs3,
            "scorecam3": score_imgs3,
        })
    return rows


def render_html(rows: list[dict]) -> str:
    # Table: [Chinese] [LayerCAM x3] [ScoreCAM x3]
    css = """
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 16px; }
    h1 { font-size: 20px; margin: 0 0 12px; }
    .meta { color: #666; font-size: 12px; margin-bottom: 16px; }
    table { border-collapse: collapse; width: 100%; table-layout: fixed; }
    thead th { position: sticky; top: 0; background: #fafafa; z-index: 1; }
    th, td { border: 1px solid #e5e5e5; vertical-align: top; padding: 6px; }
    td:first-child, th:first-child { width: 240px; }
    img.thumb { max-width: 100%; height: auto; display: block; }
    .row-title { font-weight: 600; font-size: 12px; color: #333; margin-bottom: 6px; word-break: break-all; min-height: 1em; }
    .scroller { max-height: 480px; overflow: auto; }
    """
    head = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pattern Viz Grid</title>
  <style>{css}</style>
</head>
<body>
  <h1>Pattern Viz Grid</h1>
  <div class="meta">Column 1: Chinese source. Then LayerCAM images. Then ScoreCAM images. Total rows: {len(rows)}</div>
  <table>
    <thead>
      <tr>
        <th>Source (Chinese)</th>
        <th>LayerCAM 1</th>
        <th>LayerCAM 2</th>
        <th>LayerCAM 3</th>
        <th>HiresCAM 1</th>
        <th>HiresCAM 2</th>
        <th>HiresCAM 3</th>
        <th>ScoreCAM 1</th>
        <th>ScoreCAM 2</th>
        <th>ScoreCAM 3</th>
      </tr>
    </thead>
    <tbody>
"""
    body_parts = []
    for row in rows:
        base = html.escape(row["base"])
        chinese_img = row["chinese"]
        layer_imgs3 = row["layercam3"]
        hires_imgs3 = row["hirescam3"]
        score_imgs3 = row["scorecam3"]

        cells = []

        # Column 1: Chinese source
        src_cell = f'''
          <td>
            <div class="row-title">{base}</div>
            <img class="thumb" src="{html.escape(chinese_img)}" alt="{base}">
          </td>
        '''
        cells.append(src_cell)

        # LayerCAM x3
        for p in layer_imgs3:
            if p:
                cells.append(f'<td><div class="row-title"></div><img class="thumb" src="{html.escape(p)}" alt="{base} LayerCAM"></td>')
            else:
                cells.append('<td><div class="row-title"></div></td>')

        # HiresCAM x3
        for p in hires_imgs3:
            if p:
                cells.append(f'<td><div class="row-title"></div><img class="thumb" src="{html.escape(p)}" alt="{base} HiresCAM"></td>')
            else:
                cells.append('<td><div class="row-title"></div></td>')

        # ScoreCAM x3
        for p in score_imgs3:
            if p:
                cells.append(f'<td><div class="row-title"></div><img class="thumb" src="{html.escape(p)}" alt="{base} ScoreCAM"></td>')
            else:
                cells.append('<td><div class="row-title"></div></td>')

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


