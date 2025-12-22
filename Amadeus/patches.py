from __future__ import annotations

from pathlib import Path
import site

# -----------------------------
# Patch 1: torch.load weights_only default
# -----------------------------
def patch_torch_load_weights_only_false() -> bool:
    """
    Forces torch.load to default to weights_only=False for legacy checkpoints.
    Returns True if patched, False if already patched.

    Safety: only safe if you trust the checkpoint source.
    """
    try:
        import torch
    except Exception:
        # torch not installed, nothing to patch
        return False

    original_load = torch.load

    def patched_load(*args, **kwargs):
        if "weights_only" not in kwargs:
            kwargs["weights_only"] = False
        return original_load(*args, **kwargs)

    if not getattr(torch.load, "_amadeus_patched_weights_only", False):
        patched_load._amadeus_patched_weights_only = True
        torch.load = patched_load
        return True

    return False


def apply_all_patches() -> dict[str, bool]:
    """
    Convenience function so main.py can just call one thing.
    """
    return {
        "torch_load_weights_only_false": patch_torch_load_weights_only_false(),
    }
