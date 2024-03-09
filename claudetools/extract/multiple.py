import re
import json
from xml.etree import ElementTree as ET


def extractMultipleFunctions(output_text: str):
    pattern = r"(<multiplefunctions>(.*?)</multiplefunctions>)"
    match = re.search(pattern, output_text, re.DOTALL)
    if not match:
        return None
    multiplefn = match.group(1)
    root = ET.fromstring(multiplefn)
    functions = root.findall("functioncall")
    return [json.loads(fn.text) for fn in functions]
