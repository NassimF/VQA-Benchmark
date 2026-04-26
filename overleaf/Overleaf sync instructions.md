# Overleaf Sync Instructions

## Step 1: Check status before anything

Always run this first when starting a session:

    ./check_status.sh

- No local changes and no unpushed commits → safe to run `./sync_overleaf.sh`
- Local commits ahead → run `./push_to_overleaf.sh` first
- Conflicts → resolve manually before syncing

## Pull changes from Overleaf → local

    # Default: "Update Overleaf submodule - <date>"
    ./sync_overleaf.sh

    # Custom message:
    ./sync_overleaf.sh "Your message here"

## Push local changes → Overleaf

    # Default: "Update from local - <date>"
    ./push_to_overleaf.sh

    # Custom message:
    ./push_to_overleaf.sh "Your message here"

## Note: Remotes

- The `assets/` submodule has Overleaf as its remote — LaTeX files sync here.
- The parent repo has no remote and is local only unless connected to GitHub.
