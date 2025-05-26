from typing import Callable, Dict, Tuple, Any

def xml_postprocessor_factory(tag_map: Dict[str,str]) -> Callable:
    """
    Returns an xmltodict postprocessor that will rename any key
    found in tag_map to its mapped value.
    """
    def _postprocessor(
        path: Tuple[str,...], key: str, value: Any
    ) -> Tuple[str, Any]:
        # if we have a mapping for this tag, rename it
        return (tag_map.get(key, key), value)
    return _postprocessor
