# mini-platform

A small, real example of what "platform engineering" means in practice:
not an app, but a system that *other apps run on*.

## The idea

I built a minimal version of an internal developer platform — a CLI
that takes any app with a Dockerfile and handles building, running,
port allocation, and tracking it, so the person deploying doesn't need
to know Docker commands themselves. It's a toy compared to something
built on Kubernetes with proper scaling and health checks, but as a way to 
understand good logging practices, importance of traceability and how a 
pipeline will undergo CI/CD before Devops get a hold of the image to run.

| Path | Role |
|---|---|
| `platform_cli.py` | The platform. `deploy`, `list`, `logs`, `stop`. |
| `registry.json` | Created automatically — the platform's record of what's running, where. |
| `apps/hello-app/` | An example application that meets the contract, to prove the platform works end-to-end. |
| `test_platform.py` | Tests for the parts that don't need Docker (port-picking, registry read/write). |

## Results 
Already verified, right now, without Docker: `pytest` passes (2/2), the
CLI's `--help` output is correct for every subcommand, and `deploy` fails
cleanly with a clear message when an app has no Dockerfile.

Building and running containers needs a real Docker daemon, so `deploy`, `logs`, and `stop` against a real container.

## Natural next steps (not needed before the interview)

- Add a health check: have `list` actually ping each app's port and show
  up/down status, not just "it was deployed at some point."
- Swap the Docker CLI calls for the `docker` Python SDK.
- Replace the single-host container runs with a local Kubernetes cluster
  (Minikube) so `deploy` creates a Deployment + Service instead — the
  same idea, at the next level of maturity.
