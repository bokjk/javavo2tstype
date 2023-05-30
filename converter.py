import os
import re
from pathlib import Path


def parse_java_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def convert_java_to_ts(java_filepath, ts_filepath, relative_dir):
    java_class = parse_java_file(java_filepath)
    ts_class = convert_java_class(java_class, relative_dir)
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

            convert_java_to_ts(java_filepath, ts_filepath, str(relative_dir).replace("\\", "/"))

    logger.log("Java directory to TypeScript conversion complete.")
    logger.finished()  # Emit the finished signal




def convert_java_class(java_class, relative_dir):
    classname = ""
    extends = ""
    ts_properties = []
    ts_imports = set()  # To store unique imports

    for line in java_class:
        classname_match = re.search(r'public class (\w+)', line)
        extends_match = re.search(r'public class \w+ extends (\w+)', line)
        if classname_match:
            classname = classname_match.group(1)
        if extends_match:
            extends = extends_match.group(1) + " & "
            ts_imports.add(f"import {{ {extends_match.group(1)} }} from '@type/{relative_dir}/{extends_match.group(1)}';")

        property_match = re.search(r'private (.*?) (\w+);', line)
        if property_match:
            java_type = property_match.group(1)
            ts_type_tuple = convert_java_type_to_ts_type(java_type)
            ts_type = ts_type_tuple[1]

            # If ts_type is a custom type, add an import statement
            if ts_type_tuple[0] not in ['number', 'boolean', 'string']:
                ts_imports.add(f"import {{ {ts_type_tuple[0]} }} from '@type/{relative_dir}/{ts_type_tuple[0]}';")

            ts_name = property_match.group(2)
            ts_properties.append(f"  {ts_name}?:{ts_type};  // {get_comment(line)}")

    
    imports_section = '\n'.join(ts_imports) + '\n' if ts_imports else ''
    return imports_section + f"// prettier-ignore\nexport type {classname}Type = {extends}{{\n{os.linesep.join(ts_properties)}\n}}"




def convert_java_type_to_ts_type(java_type):
    if java_type in ['int', 'long', 'float', 'double', 'Double', 'short', 'byte', 'Integer']:
        return 'number'
    elif java_type in ['boolean', 'Boolean']:
        return 'boolean'
    elif java_type in ['String', 'Date']:
        return 'string'
    elif 'List' in java_type:
        match = re.match(r'List<(.*)>', java_type)
        if match:
            inner_type = match.group(1)
            converted_type = f'{inner_type}[]'
            return (inner_type, converted_type)
    return (java_type, java_type)  # use original java type name if not matched with any known types





def get_comment(line):
    comment_match = re.search(r'//(.+)', line)
    return comment_match.group(1).strip() if comment_match else ""
