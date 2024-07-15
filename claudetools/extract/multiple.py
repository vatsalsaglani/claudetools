import re
import json
import logging
from xml.etree import ElementTree as ET
from claudetools.extract.single import extractUsingRegEx

logger = logging.getLogger(__name__)


def extractMultipleFunctions(output_text: str):
    try:
        pattern = r"(<multiplefunctions>(.*?)</multiplefunctions>)"
        match = re.search(pattern, output_text, re.DOTALL)
        logging.info(f"Multiple Function Match: {match}")
        if not match:
            return None
        multiplefn = match.group(1)
        logging.info(f"Multiple Functions Group: {multiplefn}")
        root = ET.fromstring(multiplefn)
        functions = root.findall("functioncall")
        logging.info(f"All Function Calls: {functions}")
        return [json.loads(fn.text) for fn in functions]
    except ET.ParseError:
        return extractUsingRegEx(output_text)
