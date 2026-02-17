"""
System Tray Icon — Provides a tray icon with status indicators and controls.
"""

import logging
from PIL import Image, ImageDraw, ImageFont
import pystray

logger = logging.getLogger("LoLAutoAccept")


# ── Icon Colors ──────────────────────────────────────────────────────────────
COLORS = {
    "connected": {
        "bg": (30, 215, 96),       # Vibrant green
        "border": (20, 170, 70),
        "symbol": (255, 255, 255),
    },
    "searching": {
        "bg": (255, 193, 7),       # Amber yellow
        "border": (200, 150, 0),
        "symbol": (255, 255, 255),
    },
    "disabled": {
        "bg": (120, 120, 130),     # Muted gray
        "border": (90, 90, 100),
        "symbol": (200, 200, 200),
    },
    "error": {
        "bg": (220, 53, 69),       # Red
        "border": (170, 40, 50),
        "symbol": (255, 255, 255),
    },
}


def create_icon_image(status: str = "searching", size: int = 64) -> Image.Image:
    """
    Generate a tray icon image with a color-coded circle and checkmark.

    Args:
        status: One of 'connected', 'searching', 'disabled', 'error'
        size: Icon size in pixels
    """
    colors = COLORS.get(status, COLORS["searching"])

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer circle (border)
    margin = 2
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=colors["border"],
    )

    # Inner circle (background)
    inner_margin = margin + 3
    draw.ellipse(
        [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
        fill=colors["bg"],
    )

    # Draw a checkmark symbol
    cx, cy = size // 2, size // 2
    check_points = [
        (cx - 12, cy + 2),   # Start of checkmark
        (cx - 4, cy + 10),   # Bottom of checkmark
        (cx + 14, cy - 10),  # End of checkmark
    ]

    # Scale points for different sizes
    scale = size / 64
    check_points = [(int(x * scale), int(y * scale)) for x, y in check_points]

    draw.line(check_points, fill=colors["symbol"], width=max(3, int(4 * scale)))

    return img


class TrayApp:
    """System tray application for LoL Auto-Accept."""

    def __init__(self, on_toggle=None, on_quit=None):
        """
        Args:
            on_toggle: Callback when enable/disable is toggled. Receives new state (bool).
            on_quit:   Callback when quit is selected.
        """
        self.on_toggle = on_toggle
        self.on_quit = on_quit
        self.enabled = True
        self.status_text = "Searching for League client..."
        self.matches_accepted = 0

        self.icon = pystray.Icon(
            name="LoLAutoAccept",
            icon=create_icon_image("searching"),
            title="LoL Auto-Accept\nSearching for League client...",
            menu=self._build_menu(),
        )

    def _build_menu(self):
        """Build the right-click context menu."""
        return pystray.Menu(
            pystray.MenuItem(
                text=lambda _: f"Status: {self.status_text}",
                action=None,
                enabled=False,
            ),
            pystray.MenuItem(
                text=lambda _: f"Matches accepted: {self.matches_accepted}",
                action=None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                text=lambda _: "Disable" if self.enabled else "Enable",
                action=self._toggle,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                text="Quit",
                action=self._quit,
            ),
        )

    def _toggle(self, icon, item):
        """Toggle auto-accept on/off."""
        self.enabled = not self.enabled
        logger.info(f"Auto-accept {'enabled' if self.enabled else 'disabled'}")

        if self.enabled:
            self.update_status("searching", "Searching for League client...")
        else:
            self.update_status("disabled", "Auto-accept disabled")

        if self.on_toggle:
            self.on_toggle(self.enabled)

        self.icon.update_menu()

    def _quit(self, icon, item):
        """Quit the application."""
        logger.info("Quitting application...")
        if self.on_quit:
            self.on_quit()
        self.icon.stop()

    def update_status(self, icon_status: str, text: str):
        """
        Update the tray icon appearance and tooltip.

        Args:
            icon_status: One of 'connected', 'searching', 'disabled', 'error'
            text:        Status text for the tooltip
        """
        self.status_text = text
        self.icon.icon = create_icon_image(icon_status)
        self.icon.title = f"LoL Auto-Accept\n{text}"
        self.icon.update_menu()

    def increment_matches(self):
        """Increment the accepted matches counter."""
        self.matches_accepted += 1
        self.icon.update_menu()

    def run(self):
        """Start the tray icon (blocks the calling thread)."""
        logger.info("System tray icon started.")
        self.icon.run()

    def stop(self):
        """Stop the tray icon."""
        self.icon.stop()
