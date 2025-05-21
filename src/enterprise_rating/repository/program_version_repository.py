from pathlib import Path
from xml import xml_postprocessor_factory
import xmltodict
from enterprise_rating.entities.program_version import ProgramVersion  # wherever you defined your Pydantic models


class ProgramVersionRepository:
    XML_FILE = Path("/data/C504714691.xml")

    @staticmethod
    def get_program_version(lob: str, progId: str, progVer: str) -> ProgramVersion | None:
        postproc = xml_postprocessor_factory(
            {
                "@i": "index",  # if you still want to map <element i="…">
                # any other tag renames…
            }
        )

        with open(ProgramVersionRepository.XML_FILE, encoding="utf-8") as f:
            doc = xmltodict.parse(f.read(), postprocessor=postproc, force_list=("seq",))

        progVer = doc.get("export", {})

        if progVer is None:
            return None

        # Let Pydantic coerce types, apply defaults, and validate
        return ProgramVersion.parse_obj(progVer)
