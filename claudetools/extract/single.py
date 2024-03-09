import re
import json
from xml.etree import ElementTree as ET


def extractSingleFunction(output_text: str):
    pattern = r"(<singlefunction>(.*?)</singlefunction>)"
    match = re.search(pattern, output_text, re.DOTALL)
    if not match:
        return None
    fn = match.group(1)
    root = ET.fromstring(fn)
    functions = root.findall("functioncall")
    return [json.loads(fn.text) for fn in functions]
