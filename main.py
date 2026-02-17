"""
LoL Auto-Accept — Automatically accepts League of Legends matches.

Run this script to start the background auto-accept service.
A system tray icon will appear with controls and status.
"""

import sys
import time
import logging
import threading

from lcu import LCUConnector
from tray import TrayApp

# ── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("auto_accept.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("LoLAutoAccept")

# ── Configuration ────────────────────────────────────────────────────────────
POLL_INTERVAL = 1.0        # Seconds between ready-check polls
CLIENT_SEARCH_INTERVAL = 3.0  # Seconds between client search attempts
POST_ACCEPT_COOLDOWN = 5.0    # Seconds to wait after accepting a match


class LoLAutoAccept:
    """Main application that ties the LCU connector and tray icon together."""

    def __init__(self):
        self.connector = LCUConnector()
        self.running = True
        self.enabled = True

        self.tray = TrayApp(
            on_toggle=self._on_toggle,
            on_quit=self._on_quit,
        )

    def _on_toggle(self, enabled: bool):
        """Called when the user toggles auto-accept from the tray menu."""
        self.enabled = enabled

    def _on_quit(self):
        """Called when the user quits from the tray menu."""
        self.running = False

    def _monitor_loop(self):
        """
        Background thread that continuously monitors for ready checks.
        
        State machine:
          1. If disabled → sleep and wait
          2. If not connected → search for League client
          3. If connected → poll for ready check
          4. If ready check found → accept match
        """
        logger.info("Monitor loop started. Waiting for League client...")

        while self.running:
            # ── Disabled state ───────────────────────────────────────────
            if not self.enabled:
                time.sleep(POLL_INTERVAL)
                continue

            # ── Search for client ────────────────────────────────────────
            if not self.connector.connected:
                self.tray.update_status("searching", "Searching for League client...")

                if self.connector.find_client():
                    self.tray.update_status("connected", "Connected — Auto-accepting matches")
                else:
                    time.sleep(CLIENT_SEARCH_INTERVAL)
                    continue

            # ── Verify client is still running ───────────────────────────
            if not self.connector.is_client_running():
                logger.info("League client closed. Waiting for restart...")
                self.connector.connected = False
                self.tray.update_status("searching", "League client closed. Waiting...")
                time.sleep(CLIENT_SEARCH_INTERVAL)
                continue

            # ── Poll for ready check ─────────────────────────────────────
            if self.connector.check_ready_check():
                if self.connector.accept_match():
                    self.tray.update_status("connected", "Match accepted! ✓")
                    self.tray.increment_matches()

                    # Cooldown after accepting
                    time.sleep(POST_ACCEPT_COOLDOWN)

                    # Restore normal status
                    if self.running and self.enabled:
                        self.tray.update_status("connected", "Connected — Auto-accepting matches")
                else:
                    self.tray.update_status("error", "Failed to accept match")
                    time.sleep(2)
                    if self.running and self.enabled:
                        self.tray.update_status("connected", "Connected — Auto-accepting matches")

            time.sleep(POLL_INTERVAL)

        logger.info("Monitor loop stopped.")

    def run(self):
        """Start the application."""
        logger.info("=" * 50)
        logger.info("  LoL Auto-Accept started")
        logger.info("  Check the system tray for controls")
        logger.info("=" * 50)

        # Start the monitor loop in a background thread
        monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="MonitorThread",
        )
        monitor_thread.start()

        # Run the tray icon on the main thread (required by pystray on Windows)
        try:
            self.tray.run()
        except KeyboardInterrupt:
            logger.info("Interrupted by user.")
        finally:
            self.running = False
            logger.info("Application shut down.")


def main():
    app = LoLAutoAccept()
    app.run()


if __name__ == "__main__":
    main()
