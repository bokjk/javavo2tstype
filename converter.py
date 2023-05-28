import os
import re
from pathlib import Path

def parse_java_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def convert_java_to_ts(java_filepath, ts_filepath):
    java_class = parse_java_file(java_filepath)
    ts_class = convert_java_class(java_class)
    with open(ts_filepath, 'w', encoding='utf-8') as file:  # Added encoding='utf-8'
        file.write(ts_class)

def convert_java_directory_to_ts(java_directory, ts_directory, logger):
    logger.log("Converting Java directory to TypeScript...")

    for root, dirs, files in os.walk(java_directory):
        java_files = [f for f in files if f.endswith(".java")]

        for java_file in java_files:
            java_filepath = os.path.join(root, java_file)
            relative_dir = Path(root).relative_to(java_directory)
            ts_filepath = Path(ts_directory) / relative_dir / (java_file.replace(".java", "Type.ts"))

            # Create directory if it doesn't exist
            ts_filepath.parent.mkdir(parents=True, exist_ok=True)

            convert_java_to_ts(java_filepath, ts_filepath)
            logger.log(f"Converted {java_filepath} to {ts_filepath}")

    logger.log("Java directory to TypeScript conversion complete.")
    logger.finished()  # Emit the finished signal


def convert_java_class(java_class):
    classname = ""
    extends = ""
    ts_properties = []
    for line in java_class:
        classname_match = re.search(r'public class (\w+)', line)
        extends_match = re.search(r'public class \w+ extends (\w+)', line)
        if classname_match:
            classname = classname_match.group(1)
        if extends_match:
            extends = extends_match.group(1) + "Type & "
        property_match = re.search(r'private (\w+) (\w+);', line)
        if property_match:
            ts_type = convert_java_type_to_ts_type(property_match.group(1))
            if ts_type == 'any':
                ts_type = property_match.group(1)
            ts_name = property_match.group(2)
            ts_properties.append(f"  {ts_name}?:{ts_type};  // {get_comment(line)}")
    return f"// prettier-ignore\nexport type {classname}Type = {extends}{{\n{os.linesep.join(ts_properties)}\n}}"






def convert_java_type_to_ts_type(java_type):
    if java_type in ['int', 'long', 'float', 'double', 'Double', 'short', 'byte', 'Integer']:
        return 'number'
    elif java_type in ['boolean', 'Boolean']:
        return 'boolean'
    elif java_type in ['String', 'Date']:
        return 'string'
    else:
        return java_type  # use original java type name




def get_comment(line):
    comment_match = re.search(r'//(.+)', line)
    return comment_match.group(1).strip() if comment_match else ""
