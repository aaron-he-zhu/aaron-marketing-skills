"""Load connector siblings from source without creating adjacent bytecode."""
from __future__ import annotations

import importlib.util as _importlib_util
from pathlib import Path as _Path


_ALLOWED_CONNECTOR_SIBLINGS = {"_http", "robots"}


def _load_connector_sibling(name, caller_file):
    """Return one closed sibling module without reading or writing ``.pyc``."""
    if name not in _ALLOWED_CONNECTOR_SIBLINGS:
        raise RuntimeError("connector sibling is not allowed: %s" % name)
    caller = _Path(caller_file).resolve()
    path = caller.with_name(name + ".py")
    if path.parent != caller.parent or not path.is_file():
        raise RuntimeError("connector sibling is unavailable: %s" % name)
    specification = _importlib_util.spec_from_file_location(
        "aaron_connector_" + name.lstrip("_"), path
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("connector sibling cannot be loaded: %s" % name)
    module = _importlib_util.module_from_spec(specification)
    source = path.read_bytes()
    module.__dict__["__aaron_source_bytes__"] = source
    exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
    return module
