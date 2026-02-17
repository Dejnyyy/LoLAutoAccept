"""
Generate a custom .ico file for LoL Auto-Accept.

Creates a League-themed shield + checkmark icon in multiple sizes
required for a proper Windows .ico file.
"""

from PIL import Image, ImageDraw
import math


def create_icon(size: int = 256) -> Image.Image:
    """
    Create a League of Legends themed auto-accept icon.

    Design: Gold/dark navy shield with a bold white checkmark.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size / 256  # Scale factor

    # ── Colors (League of Legends palette) ───────────────────────────────
    dark_navy = (9, 20, 40)
    gold = (200, 155, 60)
    gold_bright = (240, 200, 80)
    white = (255, 255, 255)

    # ── Shield shape (using polygon) ─────────────────────────────────────
    cx, cy = size // 2, size // 2

    # Shield outline points
    shield_outer = [
        (cx, int(12 * s)),                    # Top center
        (int(228 * s), int(50 * s)),          # Top right
        (int(220 * s), int(170 * s)),         # Mid right
        (cx, int(244 * s)),                   # Bottom center (point)
        (int(36 * s), int(170 * s)),          # Mid left
        (int(28 * s), int(50 * s)),           # Top left
    ]

    # Shield inner (slightly smaller)
    inset = int(8 * s)
    shield_inner = [
        (cx, int(12 * s) + inset),
        (int(228 * s) - inset, int(50 * s) + int(4 * s)),
        (int(220 * s) - inset, int(170 * s) - int(4 * s)),
        (cx, int(244 * s) - inset),
        (int(36 * s) + inset, int(170 * s) - int(4 * s)),
        (int(28 * s) + inset, int(50 * s) + int(4 * s)),
    ]

    # Draw shield border (gold)
    draw.polygon(shield_outer, fill=gold)

    # Draw shield fill (dark navy)
    draw.polygon(shield_inner, fill=dark_navy)

    # ── Gold accent line at top of shield ────────────────────────────────
    accent_top = [
        (cx, int(12 * s) + inset + int(2 * s)),
        (int(228 * s) - inset - int(2 * s), int(50 * s) + int(6 * s)),
        (int(220 * s) - inset - int(2 * s), int(56 * s) + int(6 * s)),
        (int(36 * s) + inset + int(2 * s), int(56 * s) + int(6 * s)),
        (int(28 * s) + inset + int(2 * s), int(50 * s) + int(6 * s)),
    ]
    draw.polygon(accent_top, fill=gold_bright)

    # ── Checkmark ────────────────────────────────────────────────────────
    # Large bold checkmark centered in the shield
    check_start = (int(75 * s), int(130 * s))      # Left start
    check_bottom = (int(115 * s), int(185 * s))     # Bottom/bend point
    check_end = (int(190 * s), int(90 * s))         # Right end (top)

    line_width = max(3, int(22 * s))

    # Draw a thicker checkmark with multiple passes for a bolder look
    draw.line([check_start, check_bottom], fill=white, width=line_width)
    draw.line([check_bottom, check_end], fill=white, width=line_width)

    # Round the joints with circles
    r = line_width // 2
    for point in [check_start, check_bottom, check_end]:
        draw.ellipse(
            [point[0] - r, point[1] - r, point[0] + r, point[1] + r],
            fill=white,
        )

    # ── Subtle gold glow around checkmark endpoints ─────────────────────
    glow_r = int(4 * s)
    for point in [check_start, check_end]:
        draw.ellipse(
            [point[0] - glow_r, point[1] - glow_r,
             point[0] + glow_r, point[1] + glow_r],
            fill=gold_bright,
        )

    return img


def main():
    """Generate the .ico file with multiple sizes."""
    # Create the base icon at high resolution
    base = create_icon(256)

    # Generate all standard Windows icon sizes
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    for sz in sizes:
        resized = base.resize((sz, sz), Image.LANCZOS)
        images.append(resized)

    # Save as .ico with all sizes embedded
    images[-1].save(
        "icon.ico",
        format="ICO",
        sizes=[(sz, sz) for sz in sizes],
        append_images=images[:-1],
    )
    print(f"✓ Created icon.ico with sizes: {sizes}")

    # Also save a PNG preview
    base.save("icon_preview.png")
    print("✓ Created icon_preview.png (256x256 preview)")


if __name__ == "__main__":
    main()
