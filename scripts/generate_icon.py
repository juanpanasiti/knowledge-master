"""Script to generate a crisp 128x128 PNG icon for Knowledge Master."""

import struct
import zlib
from pathlib import Path


def generate_png_icon(output_path: Path) -> None:
    width = 128
    height = 128
    raw_rows = []

    # Draw rounded square with indigo gradient and white open book silhouette
    for y in range(height):
        row = bytearray([0])  # Filter type 0 (None)
        for x in range(width):
            # Check corner distance for rounded rectangle (corner radius 28)
            dx = max(0, max(28 - x, x - (width - 28)))
            dy = max(0, max(28 - y, y - (height - 28)))
            is_outside = (dx * dx + dy * dy) > 28 * 28

            if is_outside:
                row.extend([0, 0, 0, 0])  # Transparent
                continue

            # Indigo gradient background: (67, 56, 202) to (99, 102, 241)
            t = y / height
            r = int(67 * (1 - t) + 99 * t)
            g = int(56 * (1 - t) + 102 * t)
            b = int(202 * (1 - t) + 241 * t)
            a = 255

            # Draw stylized open book shape in the center (y: 36 to 92, x: 30 to 98)
            # Left page: x from 34 to 62, y from 42 to 86
            # Right page: x from 66 to 94, y from 42 to 86
            is_left_page = (34 <= x <= 62 and 44 <= y <= 84 and abs(y - 84) > (x - 34) * 0.1)
            is_right_page = (66 <= x <= 94 and 44 <= y <= 84 and abs(y - 84) > (94 - x) * 0.1)
            is_spine = (62 < x < 66 and 48 <= y <= 86)
            is_bookmark = (60 <= x <= 68 and 38 <= y <= 58)

            if is_left_page or is_right_page or is_bookmark:
                r, g, b = 248, 250, 252  # Off-white
            elif is_spine:
                r, g, b = 199, 210, 254  # Light indigo spine

            row.extend([r, g, b, a])
        raw_rows.append(bytes(row))

    raw_data = b"".join(raw_rows)
    compressed_data = zlib.compress(raw_data, level=9)

    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + make_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + make_chunk(b"IDAT", compressed_data)
        + make_chunk(b"IEND", b"")
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(png_bytes)


if __name__ == "__main__":
    target = Path(__file__).parent.parent / "assets" / "icon.png"
    generate_png_icon(target)
    print(f"Icon generated at {target} ({target.stat().st_size} bytes)")
