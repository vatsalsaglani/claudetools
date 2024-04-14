import re
import json
import logging
import xml
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


def extractSingleFunction(output_text: str):
    try:
        pattern = r"(<singlefunction>(.*?)</singlefunction>)"
        match = re.search(pattern, output_text, re.DOTALL)
        logging.info(f"Single Function Match: {match}")
        if not match:
            return None
        fn = match.group(1)
        logging.info(f"Single Function Group: {fn}")
        root = ET.fromstring(fn)
        functions = root.findall("functioncall")
        logging.info(f"All Function Calls: {functions}")
        return [json.loads(fn.text) for fn in functions]
    except ET.ParseError:
        return extractUsingRegEx(output_text)


def extractUsingRegEx(output_text: str):
    pattern = r"<functioncall>\s*(\{.*?\})\s*</functioncall>"
    matches = re.findall(pattern, output_text, re.DOTALL)
    logging.info(f"Exception block Matches: {matches}")

    results = []
    for json_string in matches:
        try:
            json_data = json.loads(json_string)
            results.append(json_data)
        except json.JSONDecodeError as err:
            print(f"Error decoding JSON: {str(err)}")
            continue
    return results
