#!/usr/bin/env python3
"""
mini-platform — a tiny self-service deployment platform.

The idea: a developer doesn't need to know Docker to get their app running.
They just point this CLI at a folder containing a Dockerfile, and the
platform builds it, runs it, picks a free port, and tracks it. That's the
core job of an "Internal Developer Platform" — abstracting infrastructure
operations behind one simple, consistent interface, no matter what the
app underneath is written in.
"""

import argparse
import json
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent / "registry.json"


def load_registry():
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text())
    return {}


def save_registry(registry):
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))


def find_free_port(start=8000, end=8999):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free ports available in range")


def run(cmd):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True)


def deploy(args):
    app_path = Path(args.app_path).resolve()
    dockerfile = app_path / "Dockerfile"
    if not dockerfile.exists():
        sys.exit(
            f"No Dockerfile found in {app_path} — the platform only knows "
            "how to run apps that provide one. That's the contract."
        )

    registry = load_registry()
    if args.name in registry:
        sys.exit(f"'{args.name}' is already deployed. Run 'stop {args.name}' first, or pick a different --name.")

    image_tag = f"platform/{args.name}"
    run(["docker", "build", "-t", image_tag, str(app_path)])

    host_port = find_free_port()
    run([
        "docker", "run", "-d",
        "--name", args.name,
        "-p", f"{host_port}:{args.container_port}",
        image_tag,
    ])

    registry[args.name] = {
        "image": image_tag,
        "host_port": host_port,
        "container_port": args.container_port,
        "deployed_at": datetime.now(timezone.utc).isoformat(),
    }
    save_registry(registry)

    print(f"\nDeployed '{args.name}' — reachable at http://localhost:{host_port}")


def list_apps(args):
    registry = load_registry()
    if not registry:
        print("No apps deployed.")
        return
    for name, info in registry.items():
        print(f"{name:15} image={info['image']:25} port={info['host_port']:<6} deployed={info['deployed_at']}")


def logs(args):
    run(["docker", "logs", args.name])


def stop(args):
    registry = load_registry()
    if args.name not in registry:
        sys.exit(f"'{args.name}' is not in the registry.")
    run(["docker", "rm", "-f", args.name])
    del registry[args.name]
    save_registry(registry)
    print(f"Stopped and removed '{args.name}'.")


def main():
    parser = argparse.ArgumentParser(description="mini-platform: self-service app deployment")
    sub = parser.add_subparsers(dest="command", required=True)

    p_deploy = sub.add_parser("deploy", help="Build and run an app from a folder containing a Dockerfile")
    p_deploy.add_argument("app_path", help="Path to the app folder")
    p_deploy.add_argument("--name", required=True, help="Name to deploy the app under")
    p_deploy.add_argument("--container-port", type=int, default=5000, help="Port the app listens on inside its container")
    p_deploy.set_defaults(func=deploy)

    p_list = sub.add_parser("list", help="List currently deployed apps")
    p_list.set_defaults(func=list_apps)

    p_logs = sub.add_parser("logs", help="Show logs for a deployed app")
    p_logs.add_argument("name")
    p_logs.set_defaults(func=logs)

    p_stop = sub.add_parser("stop", help="Stop and remove a deployed app")
    p_stop.add_argument("name")
    p_stop.set_defaults(func=stop)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
