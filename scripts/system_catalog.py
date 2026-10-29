"""Ordered catalog identities for authoring generators, never a runtime oracle.

Callers retain their own source parsing, product identity and output checks.
Independent architecture/discovery checks deliberately do not use this reader.
"""
from collections import namedtuple
import re


Skill = namedtuple("Skill", "name directory discipline phase")
Group = namedtuple("Group", "discipline specification phase_order skills")
_SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")


def catalog_groups(catalog, error_type=ValueError):
    """Close catalog membership and return its declared discipline/phase order."""
    if not isinstance(catalog, dict):
        raise error_type("system catalog must be an object")
    order = catalog.get("logical_order")
    disciplines = catalog.get("disciplines")
    counts = catalog.get("counts")
    if (not isinstance(order, list) or not order
            or any(not isinstance(key, str) or not _SLUG.fullmatch(key) for key in order)
            or len(order) != len(set(order))):
        raise error_type("system catalog logical_order must be a unique slug list")
    if (not isinstance(disciplines, dict)
            or set(order) != set(disciplines) | {"protocol"}):
        raise error_type("system catalog logical_order does not cover its disciplines")
    if not isinstance(counts, dict) or type(counts.get("total_skills")) is not int:
        raise error_type("system catalog total_skills must be an integer")

    groups = []
    seen = set()
    for discipline in order:
        spec = catalog.get("protocol") if discipline == "protocol" else disciplines[discipline]
        if not isinstance(spec, dict):
            raise error_type("system catalog discipline %s is invalid" % discipline)
        if discipline == "protocol":
            phases = [("protocol", spec.get("skills"))]
        else:
            phase_order = spec.get("phase_order")
            phase_map = spec.get("phases")
            if (not isinstance(phase_order, list) or not phase_order
                    or any(not isinstance(phase, str) or not _SLUG.fullmatch(phase)
                           for phase in phase_order)
                    or len(phase_order) != len(set(phase_order))
                    or not isinstance(phase_map, dict) or set(phase_order) != set(phase_map)):
                raise error_type("system catalog phases for %s are invalid" % discipline)
            phases = [(phase, phase_map[phase]) for phase in phase_order]
        skills = []
        for phase, names in phases:
            if (not isinstance(names, list) or not names
                    or any(not isinstance(name, str) or not _SLUG.fullmatch(name) for name in names)
                    or len(names) != len(set(names))):
                raise error_type("system catalog target list %s/%s is invalid" % (discipline, phase))
            for name in names:
                if name in seen:
                    raise error_type("skill %s is covered more than once" % name)
                seen.add(name)
                directory = ("protocol/%s" % name if discipline == "protocol"
                             else "%s/%s/%s" % (discipline, phase, name))
                skills.append(Skill(name, directory, discipline, phase))
        groups.append(Group(discipline, spec, [phase for phase, _names in phases], skills))
    if len(seen) != counts["total_skills"]:
        raise error_type("catalog declares %r skills but enumerates %d"
                         % (counts["total_skills"], len(seen)))
    return groups
