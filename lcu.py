"""
LCU Connector — Finds the League client, polls for ready checks, and auto-accepts.
"""

import re
import logging
import psutil
import requests
import urllib3

# Suppress InsecureRequestWarning for self-signed LCU certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("LoLAutoAccept")


class LCUConnector:
    """Handles connection to the League Client Update (LCU) API."""

    BASE_URL = "https://127.0.0.1:{port}"
    READY_CHECK_ENDPOINT = "/lol-matchmaking/v1/ready-check"
    ACCEPT_ENDPOINT = "/lol-matchmaking/v1/ready-check/accept"
    PROCESS_NAME = "LeagueClientUx.exe"

    def __init__(self):
        self.port = None
        self.token = None
        self.connected = False
        self._session = requests.Session()
        self._session.verify = False  # LCU uses a self-signed certificate

    @property
    def base_url(self):
        return self.BASE_URL.format(port=self.port)

    def find_client(self) -> bool:
        """
        Find the running League client process and extract connection details.
        Returns True if the client was found and credentials extracted.
        """
        try:
            for proc in psutil.process_iter(["name", "cmdline"]):
                try:
                    if proc.info["name"] and proc.info["name"].lower() == self.PROCESS_NAME.lower():
                        cmdline = " ".join(proc.info["cmdline"] or [])

                        port_match = re.search(r"--app-port=(\d+)", cmdline)
                        token_match = re.search(r"--remoting-auth-token=([\w_-]+)", cmdline)

                        if port_match and token_match:
                            self.port = port_match.group(1)
                            self.token = token_match.group(1)
                            self._session.auth = ("riot", self.token)
                            self.connected = True
                            logger.info(f"Connected to League client on port {self.port}")
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logger.error(f"Error searching for League client: {e}")

        self.connected = False
        self.port = None
        self.token = None
        return False

    def check_ready_check(self) -> bool:
        """
        Poll the ready-check endpoint.
        Returns True if a ready check is active and hasn't been accepted yet.
        """
        if not self.connected:
            return False

        try:
            resp = self._session.get(
                f"{self.base_url}{self.READY_CHECK_ENDPOINT}",
                timeout=2,
            )

            if resp.status_code == 200:
                data = resp.json()
                state = data.get("state", "")
                player_response = data.get("playerResponse", "")

                if state == "InProgress" and player_response == "None":
                    logger.info("Ready check detected! Match found.")
                    return True

            return False

        except requests.exceptions.ConnectionError:
            # Client may have closed
            logger.warning("Lost connection to League client.")
            self.connected = False
            return False
        except Exception as e:
            logger.debug(f"Ready check poll error: {e}")
            return False

    def accept_match(self) -> bool:
        """
        Accept the current ready check.
        Returns True if the accept request was sent successfully.
        """
        if not self.connected:
            return False

        try:
            resp = self._session.post(
                f"{self.base_url}{self.ACCEPT_ENDPOINT}",
                timeout=2,
            )
            if resp.status_code in (200, 204):
                logger.info("✓ Match accepted successfully!")
                return True
            else:
                logger.warning(f"Accept returned status {resp.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to accept match: {e}")
            return False

    def is_client_running(self) -> bool:
        """Quick check if the League client process is still running."""
        try:
            for proc in psutil.process_iter(["name"]):
                if proc.info["name"] and proc.info["name"].lower() == self.PROCESS_NAME.lower():
                    return True
        except Exception:
            pass
        return False
