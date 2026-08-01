#!/usr/bin/env python3
"""CLI wrapper for the importable :mod:`workflow_loop` runtime."""
import importlib.util
from pathlib import Path


def _load_main():
    path = Path(__file__).with_name("workflow_loop.py")
    specification = importlib.util.spec_from_file_location("workflow_loop_runtime", path)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load scripts/workflow_loop.py")
    module = importlib.util.module_from_spec(specification)
    source = path.read_bytes()
    exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
    return module.main


main = _load_main()


if __name__ == "__main__":
    raise SystemExit(main())
