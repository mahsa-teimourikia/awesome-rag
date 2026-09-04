"""Validate coordinate-based diagram specifications and render accessible SVGs."""

from __future__ import annotations

import html
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
COLORS = {
    "service": ("#EAF1FF", "#2F6BFF"),
    "agent": ("#F0EEFF", "#7667E8"),
    "data": ("#E5F7F6", "#16A3A5"),
    "action": ("#FFF1DF", "#F59E42"),
    "operations": ("#FFFFFF", "#8A98A8"),
    "danger": ("#FFF0F0", "#D64545"),
}


def port(node: dict, name: str) -> tuple[float, float]:
    spec = node["ports"][name]
    x, y, w, h = (node[k] for k in ("x", "y", "width", "height"))
    side, offset = spec["side"], spec.get("offset", 0.5)
    return {
        "left": (x, y + h * offset), "right": (x + w, y + h * offset),
        "top": (x + w * offset, y), "bottom": (x + w * offset, y + h),
    }[side]


def validate(spec: dict) -> None:
    width, height, margin = spec["canvas"]["width"], spec["canvas"]["height"], spec["canvas"]["margin"]
    nodes = {n["id"]: n for n in spec["nodes"]}
    if len(nodes) != len(spec["nodes"]):
        raise ValueError(f"{spec['id']}: duplicate node ID")
    edge_ids = [e["id"] for e in spec["edges"]]
    if len(edge_ids) != len(set(edge_ids)):
        raise ValueError(f"{spec['id']}: duplicate edge ID")
    for node in nodes.values():
        if node["x"] < margin or node["y"] < margin or node["x"] + node["width"] > width - margin or node["y"] + node["height"] > height - margin:
            raise ValueError(f"{spec['id']}: node outside canvas: {node['id']}")
    for i, left in enumerate(spec["nodes"]):
        for right in spec["nodes"][i + 1:]:
            overlap = not (left["x"] + left["width"] <= right["x"] or right["x"] + right["width"] <= left["x"] or left["y"] + left["height"] <= right["y"] or right["y"] + right["height"] <= left["y"])
            if overlap:
                raise ValueError(f"{spec['id']}: overlap {left['id']} / {right['id']}")
    for edge in spec["edges"]:
        for endpoint in ("from", "to"):
            node_id, port_name = edge[endpoint]["node"], edge[endpoint]["port"]
            if node_id not in nodes or port_name not in nodes[node_id]["ports"]:
                raise ValueError(f"{spec['id']}: invalid edge endpoint {edge['id']}:{endpoint}")


def wrap(label: str, limit: int = 22) -> list[str]:
    words, lines, current = label.split(), [], ""
    for word in words:
        if current and len(current) + len(word) + 1 > limit:
            lines.append(current); current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines


def render(spec: dict) -> str:
    validate(spec)
    nodes = {n["id"]: n for n in spec["nodes"]}
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{spec['canvas']['width']}" height="{spec['canvas']['height']}" viewBox="0 0 {spec['canvas']['width']} {spec['canvas']['height']}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(spec['title'])}</title><desc id="desc">{html.escape(spec['alt_text'])}</desc>
<defs><filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#16324F" flood-opacity="0.10"/></filter></defs>
<rect width="100%" height="100%" fill="{spec['canvas']['background']}"/>
<text x="{spec['canvas']['margin']}" y="70" font-family="Inter,Arial,sans-serif" font-size="34" font-weight="700" fill="#16324F">{html.escape(spec['title'])}</text>
<text x="{spec['canvas']['margin']}" y="103" font-family="Inter,Arial,sans-serif" font-size="17" fill="#52606D">{html.escape(spec['subtitle'])}</text>''']
    for group in spec.get("groups", []):
        parts.append(f'<rect x="{group["x"]}" y="{group["y"]}" width="{group["width"]}" height="{group["height"]}" rx="20" fill="{group.get("fill", "#FFFFFF")}" stroke="#D7DEE8" stroke-width="2" stroke-dasharray="7 7"/><text x="{group["x"] + 20}" y="{group["y"] + 32}" font-family="Inter,Arial,sans-serif" font-size="15" font-weight="700" fill="#52606D">{html.escape(group["label"].upper())}</text>')
    for node in spec["nodes"]:
        fill, stroke = COLORS[node.get("type", "operations")]
        parts.append(f'<rect x="{node["x"]}" y="{node["y"]}" width="{node["width"]}" height="{node["height"]}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="2.5" filter="url(#shadow)"/>')
        lines = wrap(node["label"], node.get("wrap", 22))
        line_height = 24
        start_y = node["y"] + node["height"] / 2 - ((len(lines)-1)*line_height)/2 + 7
        for idx, line in enumerate(lines):
            parts.append(f'<text x="{node["x"] + node["width"] / 2}" y="{start_y + idx*line_height}" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="18" font-weight="700" fill="#16324F">{html.escape(line)}</text>')
        if node.get("subtitle"):
            parts.append(f'<text x="{node["x"] + node["width"] / 2}" y="{node["y"] + node["height"] - 17}" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="13" fill="#52606D">{html.escape(node["subtitle"])}</text>')
    # Render connectors after nodes so arrowheads remain visibly attached to the
    # target boundary instead of being hidden beneath the target rectangle.
    for edge in spec["edges"]:
        start = port(nodes[edge["from"]["node"]], edge["from"]["port"])
        end = port(nodes[edge["to"]["node"]], edge["to"]["port"])
        points = [start] + [tuple(p) for p in edge.get("route", [])] + [end]
        data = " ".join(("M" if idx == 0 else "L") + f" {x} {y}" for idx, (x, y) in enumerate(points))
        parts.append(f'<path d="{data}" fill="none" stroke="#52606D" stroke-width="2.5" stroke-linejoin="round"/>')
        end_x, end_y = end
        previous_x, previous_y = next(
            point for point in reversed(points[:-1]) if point != end
        )
        length = math.hypot(end_x - previous_x, end_y - previous_y)
        unit_x, unit_y = (end_x - previous_x) / length, (end_y - previous_y) / length
        base_x, base_y = end_x - 13 * unit_x, end_y - 13 * unit_y
        perpendicular_x, perpendicular_y = -unit_y * 6, unit_x * 6
        arrow = (
            f"{end_x},{end_y} "
            f"{base_x + perpendicular_x},{base_y + perpendicular_y} "
            f"{base_x - perpendicular_x},{base_y - perpendicular_y}"
        )
        parts.append(f'<polygon points="{arrow}" fill="#52606D"/>')
        if edge.get("label"):
            lx, ly = edge.get("label_at", points[len(points)//2])
            parts.append(f'<rect x="{lx-70}" y="{ly-15}" width="140" height="26" rx="8" fill="#F7F9FC"/><text x="{lx}" y="{ly+4}" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="14" fill="#52606D">{html.escape(edge["label"])}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    for path in sorted(HERE.glob("*.spec.json")):
        spec = json.loads(path.read_text())
        output = HERE / spec["output"]
        output.write_text(render(spec), encoding="utf-8")
        print(f"validated and rendered {output.name}")
