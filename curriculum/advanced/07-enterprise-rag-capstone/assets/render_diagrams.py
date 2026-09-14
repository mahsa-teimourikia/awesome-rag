"""Validate coordinate-based diagram specifications and render accessible SVGs."""

from __future__ import annotations

import html
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
def port(node: dict, name: str) -> tuple[float, float]:
    spec = node["ports"][name]
    x, y, w, h = (node[k] for k in ("x", "y", "width", "height"))
    side, offset = spec["side"], spec.get("offset", 0.5)
    return {
        "left": (x, y + h * offset), "right": (x + w, y + h * offset),
        "top": (x + w * offset, y), "bottom": (x + w * offset, y + h),
    }[side]


def bounds(item: dict) -> tuple[float, float, float, float]:
    """Return left, top, right, and bottom coordinates."""
    return (
        item["x"], item["y"],
        item["x"] + item["width"], item["y"] + item["height"],
    )


def rectangles_overlap(left: dict, right: dict, clearance: float = 0) -> bool:
    lx1, ly1, lx2, ly2 = bounds(left)
    rx1, ry1, rx2, ry2 = bounds(right)
    return not (
        lx2 + clearance <= rx1 or rx2 + clearance <= lx1
        or ly2 + clearance <= ry1 or ry2 + clearance <= ly1
    )


def segment_crosses_box(
    start: tuple[float, float], end: tuple[float, float], box: dict, clearance: float = 8
) -> bool:
    """Detect an orthogonal segment crossing a box's protected interior."""
    x1, y1, x2, y2 = bounds(box)
    x1 -= clearance; y1 -= clearance; x2 += clearance; y2 += clearance
    sx, sy = start; ex, ey = end
    if sx == ex:
        low, high = sorted((sy, ey))
        return x1 < sx < x2 and max(low, y1) < min(high, y2)
    if sy == ey:
        low, high = sorted((sx, ex))
        return y1 < sy < y2 and max(low, x1) < min(high, x2)
    raise ValueError(f"non-orthogonal segment: {start} -> {end}")


def route_points(edge: dict, nodes: dict[str, dict]) -> list[tuple[float, float]]:
    points = [port(nodes[edge["from"]["node"]], edge["from"]["port"])]
    points.extend(tuple(point) for point in edge.get("route", []))
    points.append(port(nodes[edge["to"]["node"]], edge["to"]["port"]))
    return [point for index, point in enumerate(points) if index == 0 or point != points[index - 1]]


def direction_is_valid(side: str, boundary: tuple[float, float], adjacent: tuple[float, float]) -> bool:
    bx, by = boundary; ax, ay = adjacent
    if side == "right":
        return by == ay and ax >= bx
    if side == "left":
        return by == ay and ax <= bx
    if side == "bottom":
        return bx == ax and ay >= by
    if side == "top":
        return bx == ax and ay <= by
    return False


def validate(spec: dict) -> None:
    width, height, margin = spec["canvas"]["width"], spec["canvas"]["height"], spec["canvas"]["margin"]
    nodes = {n["id"]: n for n in spec["nodes"]}
    if len(nodes) != len(spec["nodes"]):
        raise ValueError(f"{spec['id']}: duplicate node ID")
    edge_ids = [e["id"] for e in spec["edges"]]
    if len(edge_ids) != len(set(edge_ids)):
        raise ValueError(f"{spec['id']}: duplicate edge ID")
    groups = {group["id"]: group for group in spec.get("groups", [])}
    if len(groups) != len(spec.get("groups", [])):
        raise ValueError(f"{spec['id']}: duplicate group ID")
    semantic_colors = spec["style"]["semantic_colors"]
    for node in nodes.values():
        if node.get("type", "operations") not in semantic_colors:
            raise ValueError(f"{spec['id']}: no semantic color for {node['id']}")
        if node["x"] < margin or node["y"] < margin or node["x"] + node["width"] > width - margin or node["y"] + node["height"] > height - margin:
            raise ValueError(f"{spec['id']}: node outside canvas: {node['id']}")
        if node.get("group"):
            group = groups.get(node["group"])
            if group is None:
                raise ValueError(f"{spec['id']}: unknown group for {node['id']}")
            nx1, ny1, nx2, ny2 = bounds(node); gx1, gy1, gx2, gy2 = bounds(group)
            if not (gx1 + 20 <= nx1 and gy1 + 54 <= ny1 and nx2 <= gx2 - 20 and ny2 <= gy2 - 20):
                raise ValueError(f"{spec['id']}: {node['id']} escapes group {group['id']}")
        label_limit = node.get("wrap", max(8, int((node["width"] - 32) / 10)))
        label_lines = wrap(node["label"], label_limit)
        subtitle_lines = wrap(node.get("subtitle", ""), max(10, int((node["width"] - 28) / 7.2)))
        text_height = len(label_lines) * 24 + (8 + len(subtitle_lines) * 17 if subtitle_lines else 0)
        if text_height > node["height"] - 20:
            raise ValueError(f"{spec['id']}: text does not fit node {node['id']}")
    for i, left in enumerate(spec["nodes"]):
        for right in spec["nodes"][i + 1:]:
            if rectangles_overlap(left, right):
                raise ValueError(f"{spec['id']}: overlap {left['id']} / {right['id']}")
    for edge in spec["edges"]:
        for endpoint in ("from", "to"):
            node_id, port_name = edge[endpoint]["node"], edge[endpoint]["port"]
            if node_id not in nodes or port_name not in nodes[node_id]["ports"]:
                raise ValueError(f"{spec['id']}: invalid edge endpoint {edge['id']}:{endpoint}")
        points = route_points(edge, nodes)
        if len(points) < 2:
            raise ValueError(f"{spec['id']}: empty route {edge['id']}")
        for start, end in zip(points, points[1:]):
            if start[0] != end[0] and start[1] != end[1]:
                raise ValueError(f"{spec['id']}: diagonal route {edge['id']}: {start} -> {end}")
        source_node = nodes[edge["from"]["node"]]
        target_node = nodes[edge["to"]["node"]]
        source_side = source_node["ports"][edge["from"]["port"]]["side"]
        target_side = target_node["ports"][edge["to"]["port"]]["side"]
        if not direction_is_valid(source_side, points[0], points[1]):
            raise ValueError(f"{spec['id']}: route {edge['id']} leaves its source through the wrong side")
        if not direction_is_valid(target_side, points[-1], points[-2]):
            raise ValueError(f"{spec['id']}: route {edge['id']} approaches its target through the wrong side")
        endpoint_ids = {edge["from"]["node"], edge["to"]["node"]}
        for node_id, node in nodes.items():
            if node_id in endpoint_ids:
                continue
            for start, end in zip(points, points[1:]):
                if segment_crosses_box(start, end, node):
                    raise ValueError(f"{spec['id']}: route {edge['id']} crosses node {node_id}")
        if edge.get("label"):
            lx, ly = edge["label_at"]
            label_width = edge.get("label_width", max(88, len(edge["label"]) * 8 + 24))
            label_box = {"x": lx - label_width / 2, "y": ly - 18, "width": label_width, "height": 32}
            for node_id, node in nodes.items():
                if rectangles_overlap(label_box, node, clearance=6):
                    raise ValueError(f"{spec['id']}: label for {edge['id']} overlaps node {node_id}")


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
    style = spec["style"]
    font = style["font_family"]
    title_color = style["title_color"]
    connector_color = style["connector_color"]
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{spec['canvas']['width']}" height="{spec['canvas']['height']}" viewBox="0 0 {spec['canvas']['width']} {spec['canvas']['height']}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(spec['title'])}</title><desc id="desc">{html.escape(spec['alt_text'])}</desc>
<defs><filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#16324F" flood-opacity="0.10"/></filter></defs>
<rect width="100%" height="100%" fill="{spec['canvas']['background']}"/>
<text x="{spec['canvas']['margin']}" y="70" font-family="{font}" font-size="34" font-weight="700" fill="{title_color}">{html.escape(spec['title'])}</text>
<text x="{spec['canvas']['margin']}" y="103" font-family="{font}" font-size="17" fill="#52606D">{html.escape(spec['subtitle'])}</text>''']
    for group in spec.get("groups", []):
        parts.append(f'<rect x="{group["x"]}" y="{group["y"]}" width="{group["width"]}" height="{group["height"]}" rx="20" fill="{group.get("fill", "#FFFFFF")}" stroke="#D7DEE8" stroke-width="2" stroke-dasharray="7 7"/><text x="{group["x"] + 20}" y="{group["y"] + 32}" font-family="{font}" font-size="15" font-weight="700" fill="#52606D">{html.escape(group["label"].upper())}</text>')
    # Connectors are rendered before cards. Their endpoints remain attached to
    # declared ports while cards mask any sub-pixel intrusion at the boundary.
    for edge in spec["edges"]:
        points = route_points(edge, nodes)
        data = " ".join(("M" if idx == 0 else "L") + f" {x} {y}" for idx, (x, y) in enumerate(points))
        parts.append(f'<path d="{data}" fill="none" stroke="{connector_color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')
        end_x, end_y = points[-1]
        previous_x, previous_y = points[-2]
        length = math.hypot(end_x - previous_x, end_y - previous_y)
        unit_x, unit_y = (end_x - previous_x) / length, (end_y - previous_y) / length
        base_x, base_y = end_x - 13 * unit_x, end_y - 13 * unit_y
        perpendicular_x, perpendicular_y = -unit_y * 6, unit_x * 6
        arrow = (
            f"{end_x},{end_y} "
            f"{base_x + perpendicular_x},{base_y + perpendicular_y} "
            f"{base_x - perpendicular_x},{base_y - perpendicular_y}"
        )
        parts.append(f'<polygon points="{arrow}" fill="{connector_color}"/>')
    for node in spec["nodes"]:
        color = style["semantic_colors"][node.get("type", "operations")]
        fill, stroke = color["fill"], color["stroke"]
        parts.append(f'<rect x="{node["x"]}" y="{node["y"]}" width="{node["width"]}" height="{node["height"]}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="2.5" filter="url(#shadow)"/>')
        label_lines = wrap(node["label"], node.get("wrap", max(8, int((node["width"] - 32) / 10))))
        subtitle_lines = wrap(node.get("subtitle", ""), max(10, int((node["width"] - 28) / 7.2)))
        total_height = len(label_lines) * 24 + (8 + len(subtitle_lines) * 17 if subtitle_lines else 0)
        cursor_y = node["y"] + (node["height"] - total_height) / 2 + 18
        for line in label_lines:
            parts.append(f'<text x="{node["x"] + node["width"] / 2}" y="{cursor_y}" text-anchor="middle" font-family="{font}" font-size="18" font-weight="700" fill="{title_color}">{html.escape(line)}</text>')
            cursor_y += 24
        if subtitle_lines:
            cursor_y += 4
            for line in subtitle_lines:
                parts.append(f'<text x="{node["x"] + node["width"] / 2}" y="{cursor_y}" text-anchor="middle" font-family="{font}" font-size="13" fill="#52606D">{html.escape(line)}</text>')
                cursor_y += 17
    # Edge labels sit above routes but are validated against all node bounds.
    for edge in spec["edges"]:
        if edge.get("label"):
            lx, ly = edge["label_at"]
            label_width = edge.get("label_width", max(88, len(edge["label"]) * 8 + 24))
            parts.append(f'<rect x="{lx-label_width/2}" y="{ly-18}" width="{label_width}" height="32" rx="8" fill="#F7F9FC"/><text x="{lx}" y="{ly+4}" text-anchor="middle" font-family="{font}" font-size="14" font-weight="600" fill="#52606D">{html.escape(edge["label"])}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    for path in sorted(HERE.glob("*.spec.json")):
        spec = json.loads(path.read_text())
        output = HERE / spec["output"]
        output.write_text(render(spec), encoding="utf-8")
        print(f"validated and rendered {output.name}")
