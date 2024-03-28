import re
import json
import logging
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


def extractSingleFunction(output_text: str):
    pattern = r"(<singlefunction>(.*?)</singlefunction>)"
    match = re.search(pattern, output_text, re.DOTALL)
    logging.info(f"Single Function Match: {match}")
    if not match:
        return None
    fn = match.group(1)
    logging.info(f"Multiple Function Group: {fn}")
    root = ET.fromstring(fn)
    functions = root.findall("functioncall")
    logging.info(f"All Function Calls: {functions}")
    return [json.loads(fn.text) for fn in functions]
