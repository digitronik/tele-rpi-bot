"""Immich server commands."""

import os
import subprocess
from pathlib import Path

IMMICH_DIR_PATH = Path(os.environ.get("IMMICH_DIR_PATH", "."))


def get_immich_status():
    """Retrieves the status of containers managed by Docker Compose for immich server.

    Returns:
        str: A formatted string with the names and statuses of the containers.
    """
    try:
        # Run the docker compose ps command and capture the output
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "table {{.Name}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            check=True,
            cwd=IMMICH_DIR_PATH,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"


def stop_immich_services():
    """Stops all containers managed by Docker Compose for immich server.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        result = subprocess.run(
            ["docker", "compose", "down"],
            capture_output=True,
            text=True,
            check=True,
            cwd=IMMICH_DIR_PATH,
        )
        if result.returncode == 0:
            return "Successfully stopped Immich services."
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"


def start_immich_services():
    """Starts all containers managed by Docker Compose in detached mode for immich server.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            capture_output=True,
            text=True,
            check=True,
            cwd=IMMICH_DIR_PATH,
        )
        if result.returncode == 0:
            return "Successfully started Immich services."
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
