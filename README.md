# mini-platform

A small, real example of what "platform engineering" means in practice:
not an app, but a system that *other apps run on*.

## The idea

Application teams shouldn't need to know Docker internals, which port is
free, or how to wire up a container, just to get something running. This
platform takes care of all of that behind one command. The only thing an
app has to provide is a `Dockerfile` — that's the platform's **contract**.
Meet it, and you can be deployed; it doesn't matter what language or
framework you used.

This is a miniature version of what real internal platforms (and managed
ones like Heroku, or an internal setup built on Kubernetes) do at scale.

## What's here

| Path | Role |
|---|---|
| `platform_cli.py` | The platform. `deploy`, `list`, `logs`, `stop`. |
| `registry.json` | Created automatically — the platform's record of what's running, where. |
| `apps/hello-app/` | An example application that meets the contract, to prove the platform works end-to-end. |
| `test_platform.py` | Tests for the parts that don't need Docker (port-picking, registry read/write). |

Already verified, right now, without Docker: `pytest` passes (2/2), the
CLI's `--help` output is correct for every subcommand, and `deploy` fails
cleanly with a clear message when an app has no Dockerfile.

## What you still need to do yourself

Building and running containers needs a real Docker daemon, which isn't
available in this chat environment — so `deploy`, `logs`, and `stop`
against a real container are untested here. You'll need **Docker Desktop**
installed and running on your own machine to see those work end to end.

## Try it on your machine (~5 minutes)

```bash
cd mini-platform
pip install -r apps/hello-app/requirements.txt   # only needed if you want to run hello-app outside the platform too

# Deploy the example app through the platform
python3 platform_cli.py deploy apps/hello-app --name hello

# See it running
python3 platform_cli.py list
curl http://localhost:<the port it printed>

# Check its logs
python3 platform_cli.py logs hello

# Tear it down
python3 platform_cli.py stop hello
```

Then try the real test: write a *second*, different app (any language,
as long as it has a `Dockerfile`), drop it in `apps/`, and deploy it the
same way, with no changes to `platform_cli.py`. That's the whole point —
the platform doesn't care what's inside, only that the contract is met.

## How to talk about this in the interview

If it comes up, the accurate, honest framing is:

> "I built a minimal version of an internal developer platform — a CLI
> that takes any app with a Dockerfile and handles building, running,
> port allocation, and tracking it, so the person deploying doesn't need
> to know Docker commands themselves. It's a toy compared to something
> built on Kubernetes with proper scaling and health checks, but building
> it hands-on is what made concepts like 'self-service' and 'platform as
> a contract' click for me, rather than just reading about them."

That's a stronger answer than claiming production-scale experience you
don't have yet — it shows genuine understanding and intellectual honesty,
both of which matter more at this stage than polish.

## Natural next steps (not needed before the interview)

- Add a health check: have `list` actually ping each app's port and show
  up/down status, not just "it was deployed at some point."
- Swap the Docker CLI calls for the `docker` Python SDK.
- Replace the single-host container runs with a local Kubernetes cluster
  (Minikube) so `deploy` creates a Deployment + Service instead — the
  same idea, at the next level of maturity.
