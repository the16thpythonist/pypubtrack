from typing import Iterable, Dict, Any


def exclude_keys(d: Dict[Any, Any], keys: Iterable[Any]) -> Dict[Any, Any]:
    copy = d.copy()
    for key in keys:
        del copy[key]

    return copy
