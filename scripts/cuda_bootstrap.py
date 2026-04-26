import os
import sys


def configure_conda_cuda_dlls():
    if os.name != "nt":
        return []

    env_root = sys.prefix
    candidates = [
        os.path.join(env_root, "Library", "bin"),
        os.path.join(env_root, "DLLs"),
    ]

    existing = os.environ.get("PATH", "")
    path_parts = [p for p in existing.split(os.pathsep) if p]
    normalized = {os.path.normcase(os.path.abspath(p)) for p in path_parts}
    added = []

    for candidate in candidates:
        if not os.path.isdir(candidate):
            continue

        normalized_candidate = os.path.normcase(os.path.abspath(candidate))
        if normalized_candidate in normalized:
            continue

        added.append(candidate)
        normalized.add(normalized_candidate)

    if added:
        os.environ["PATH"] = os.pathsep.join(added + path_parts)

    return added
