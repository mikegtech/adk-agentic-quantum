import logging
import os
from pathlib import Path

import xmltodict

from enterprise_rating.entities.program_version import ProgramVersion  # wherever you defined your Pydantic models

logger = logging.getLogger(__name__)


class ProgramVersionRepository:  # noqa: D101
    env_xml = os.environ.get("PROGRAM_VERSION_XML")
    if env_xml is None:
        raise RuntimeError(
            "Environment variable 'PROGRAM_VERSION_XML' is not set."
        )
    XML_FILE = Path(env_xml)

    # Define attribute maps per entity
    ATTRIBUTE_MAPS = {
        "ProgramVersion": {
            "@sub": "subscriber",
            "@line": "line",
            "@schema": "schema_id",
            "@prog": "program_id",
            "@ver": "version",
            "@verName": "version_name",
            "@pk": "primary_key",
            "@gpk": "global_primary_key",
            "@ed": "effective_date",
            "@ed_exact": "effective_date_exact",
            "@persisted": "persisted",
            "@date_mask": "date_mask",
            "@culture": "culture",
            "@decimal_symbol": "decimal_symbol",
            "@group_symbol": "group_symbol",
            "schema": "data_dictionary",
            "seq": "algorithm_seq",
            # Add more attribute mappings specific to ProgramVersion
        },
        "DataDictionary": {
            "schema": "data_dictionary",
            # Example: "@id": "schema_id",
            # Add attribute mappings specific to DataDictionary if needed
        },
        "Category": {"@l": "line", "@i": "index", "@p": "parent", "@d": "description"},
        "Input": {
            "@l": "line",
            "@i": "index",
            "@dt": "data_type",
            "@d": "description",
            "@qt": "qual_type",
            "@c": "category_id",
            "@sys": "system_var",
        },
        "AlgorithmSequence": {
            "seq": "algorithm_seq",
            "@n": "sequence_number",
            "@u": "universal",
            # Example: "@id": "schema_id",
            # Add attribute mappings specific to DataDictionary if needed
        },
        "Algorithm": {
            "item": "algorithm",
            "@pk": "prog_key",
            "@rk": "revision_key",
            "@alg": "alg_type",
            "@qt": "qual_type",
            "@cat": "category_id",
            "@d": "description",
            "@dlm": "date_last_modified",
            "@i": "index",
            "@v": "version",
            "@p": "program_id",
            "@assign_fltr": "assign_filter",
            "@adv_type": "advanced_type",
            "d": "dependency_vars",
        },
        "DependencyBase": {
            "@pk": "prog_key",
            "@rk": "revision_key",
            "@i": "index",
            "@v": "version",
            "@cid": "custom_id",
            "@d": "description",
            "@alg": "alg_type",
            "@cat": "category_id",
            "@p": "program_id",
            "@dt": "data_type",
            "@t": "type",
            "@dlm": "date_last_modified",
            "@u": "universal",
            "@level": "level_id",
            "d": "dependency_vars",
            # Add more attribute mappings specific to DependencyBase if needed
        },
        # Add more entities and their attribute maps as needed
    }

    @staticmethod
    def _entity_aware_postprocessor(path, key, value):
        # Unwrap {"item": {...}} at any level
        if isinstance(value, dict) and set(value.keys()) == {"item"}:
            value = value["item"]

        attr_map = {}
        # Determine the entity type based on the path
        if path and isinstance(path[-1], tuple):
            parent = path[-1][0]
            if parent == "export":
                attr_map = ProgramVersionRepository.ATTRIBUTE_MAPS.get("ProgramVersion", {})
            elif parent == "schema":
                attr_map = ProgramVersionRepository.ATTRIBUTE_MAPS.get("DataDictionary", {})
            elif parent == "categories":
                attr_map = ProgramVersionRepository.ATTRIBUTE_MAPS.get("Category", {})
            elif parent == "inputs":
                attr_map = ProgramVersionRepository.ATTRIBUTE_MAPS.get("Input", {})
            elif parent == "seq":
                attr_map = ProgramVersionRepository.ATTRIBUTE_MAPS.get("AlgorithmSequence", {})
            elif parent == "item":
                attr_map = ProgramVersionRepository.ATTRIBUTE_MAPS.get("Algorithm", {})
            elif parent == "d":
                attr_map = ProgramVersionRepository.ATTRIBUTE_MAPS.get("DependencyBase", {})

        mapped_key = attr_map.get(key, key)

        # Flatten categories and inputs, and map their children
        if mapped_key == "categories" and isinstance(value, dict) and "c" in value:
            value = value["c"]
            # Map each category dict's keys
            if isinstance(value, list):
                value = [
                    {ProgramVersionRepository.ATTRIBUTE_MAPS["Category"].get(k, k): v for k, v in item.items()}
                    for item in value
                ]
            elif isinstance(value, dict):
                value = [{ProgramVersionRepository.ATTRIBUTE_MAPS["Category"].get(k, k): v for k, v in value.items()}]

        if mapped_key == "inputs" and isinstance(value, dict) and "iv" in value:
            value = value["iv"]
            # Map each input dict's keys
            if isinstance(value, list):
                value = [
                    {ProgramVersionRepository.ATTRIBUTE_MAPS["Input"].get(k, k): v for k, v in item.items()}
                    for item in value
                ]
            elif isinstance(value, dict):
                value = [{ProgramVersionRepository.ATTRIBUTE_MAPS["Input"].get(k, k): v for k, v in value.items()}]

        # Flatten algorithm_seq and map their children
        if mapped_key == "algorithm" and isinstance(value, dict) and "item" in value:
            value = value["item"]
            # Map each category dict's keys
            if isinstance(value, list):
                value = [
                    {ProgramVersionRepository.ATTRIBUTE_MAPS["Algorithm"].get(k, k): v for k, v in item.items()}
                    for item in value
                ]
            elif isinstance(value, dict):
                value = [{ProgramVersionRepository.ATTRIBUTE_MAPS["Algorithm"].get(k, k): v for k, v in value.items()}]

        # Recursively map dependency_vars for nested <d> elements
        if mapped_key == "dependency_vars" and value:
            dep_map = ProgramVersionRepository.ATTRIBUTE_MAPS["DependencyBase"]

            def map_dependency(item):
                if isinstance(item, list):
                    # Recursively map and flatten
                    flat = []
                    for subitem in item:
                        mapped = map_dependency(subitem)
                        if isinstance(mapped, list):
                            flat.extend(mapped)
                        else:
                            flat.append(mapped)
                    return flat
                elif isinstance(item, dict):
                    mapped = {dep_map.get(k, k): v for k, v in item.items()}
                    if "dependency_vars" in mapped and mapped["dependency_vars"]:
                        mapped["dependency_vars"] = map_dependency(mapped["dependency_vars"])
                    return mapped
                else:
                    return item  # fallback for unexpected types

            # Always convert to a dict[int, dict]
            def to_dict_by_index(dep_list):
                result = {}
                for i, item in enumerate(dep_list):
                    # If item is a dict with a single key and that value is a dict, unwrap it
                    if isinstance(item, dict) and len(item) == 1 and isinstance(next(iter(item.values())), dict):
                        key, value = next(iter(item.items()))
                        result[str(key)] = value
                    else:
                        # Use 'index' if present, else enumerate
                        if isinstance(item, dict) and "index" in item:
                            key = str(item["index"])
                        else:
                            key = str(i)
                        result[key] = item
                return result

            if isinstance(value, dict):
                value = to_dict_by_index([map_dependency(value)])
            elif isinstance(value, list):
                mapped = map_dependency(value)
                # flatten if needed
                if isinstance(mapped, list) and any(isinstance(i, list) for i in mapped):
                    flat = []
                    for i in mapped:
                        if isinstance(i, list):
                            flat.extend(i)
                        else:
                            flat.append(i)
                    mapped = flat
                value = to_dict_by_index(mapped)

        return mapped_key, value


    @staticmethod
    def get_program_version(lob: str, progId: str, progVer: str) -> ProgramVersion | None:
        with open(ProgramVersionRepository.XML_FILE, encoding="utf-8") as f:
            doc = xmltodict.parse(
                f.read(), postprocessor=ProgramVersionRepository._entity_aware_postprocessor, force_list=("seq",)
            )

        progver_data = doc.get("export", {})

        if progver_data is None:
            return None

        # Extract the relevant data for the ProgramVersion entity
        # Let Pydantic coerce types, apply defaults, and validate
        return ProgramVersion.model_validate(progver_data)
