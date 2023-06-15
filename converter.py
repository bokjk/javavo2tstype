import os
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logging.info('This will get logged')


def find_file_path(directory, target_filename):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename == target_filename:
                relative_path = os.path.relpath(root, directory)
                return relative_path.replace(os.sep, '/')
    return None


def parse_java_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def convert_java_to_ts(java_filepath, ts_filepath, relative_dir, java_directory, prefixType):
    java_class = parse_java_file(java_filepath)
    ts_class = convert_java_class(java_class, relative_dir, java_directory, prefixType)
    with open(ts_filepath, 'w', encoding='utf-8') as file:  # Added encoding='utf-8'
        file.write(ts_class)

def convert_java_directory_to_ts(java_directory, ts_directory, logger, prefixType):
    logger.log("Converting Java directory to TypeScript...")

    for root, dirs, files in os.walk(java_directory):
        java_files = [f for f in files if f.endswith(".java")]

        if 'vo' in root or 'entity' in root:  # Check if the root directory contains 'vo' or 'entity'
            for java_file in java_files:
                java_filepath = os.path.join(root, java_file)
                relative_dir = Path(root).relative_to(java_directory)
                ts_filepath = Path(ts_directory) / relative_dir / (java_file.replace(".java", ".ts"))

                logger.log(java_filepath)
                # Create directory if it doesn't exist
                ts_filepath.parent.mkdir(parents=True, exist_ok=True)

                convert_java_to_ts(java_filepath, ts_filepath, relative_dir, java_directory, prefixType)


    logger.log("Java directory to TypeScript conversion complete.")
    logger.finished()  # Emit the finished signal




def convert_java_class(java_class, relative_dir, java_directory, prefixType):
    classname = ""
    extends = ""
    ts_properties = []
    ts_imports = set()  # To store unique imports
    # prefixType = '@type2'

    for line in java_class:
        classname_match = re.search(r'public class (\w+)', line)
        extends_match = re.search(r'public class \w+ extends (\w+)', line)

        if classname_match:
            classname = classname_match.group(1)
        if extends_match:
            target_class_path = find_file_path(java_directory, f"{extends_match.group(1)}.java")
            formatted_path = str(target_class_path).replace('\\', '/')

            extends = extends_match.group(1) + " & "
            ts_imports.add(f"import {{ {extends_match.group(1)} }} from '{prefixType}/{formatted_path}/{extends_match.group(1)}';")

        # property_match = re.search(r'private (.*?) (.*?);', line)
        property_match = re.search(r'^\s*private (.*?) (.*?);', line)
        if property_match:
            java_type = property_match.group(1)
            ts_type_tuple = convert_java_type_to_ts_type(java_type)

                
            if ts_type_tuple in ['number', 'boolean', 'string','number[]', 'boolean[]', 'string[]', 'any', 'any[]']: 
                ts_type = ts_type_tuple
            else:
                ts_type = ts_type_tuple[1]
 
            
            # If ts_type is a custom type, add an import statement
            if ts_type_tuple not in ['number', 'boolean', 'string','number[]', 'boolean[]', 'string[]', 'any', 'any[]']:
                target_class_path = find_file_path(java_directory, f"{ts_type_tuple[0]}.java")
                if ts_type_tuple[0] not in ['any', 'any[]']:

                    if classname not in ts_type_tuple[0]:
                        # logging.info(ts_type)

                        if target_class_path is not None:
                            formatted_path = target_class_path.replace('\\', '/')
                            ts_imports.add(f"import {{ {ts_type_tuple[0]} }} from '{prefixType}/{formatted_path}/{ts_type_tuple[0]}';")
                        else:
                            formatted_path = str(relative_dir).replace('\\', '/')
                            ts_imports.add(f"import {{ {ts_type_tuple[0]} }} from '{prefixType}/{formatted_path}/{ts_type_tuple[0]}';")


            # if ts_type in ['any[]']:
            # if ts_type in 'n':
            #     logging.info('-------------------')
            #     logging.info(ts_type_tuple)
            #     logging.info(ts_type)
            #     logging.info('-------------------')

            properties = property_match.group(2).split(",")
                
            for prop in properties:
                ts_name = prop.strip().split(" ")[-1]
                ts_properties.append(f"  {ts_name}?:{ts_type};  // {get_comment(line)}")
    
    imports_section = '\n'.join(ts_imports) + '\n' if ts_imports else ''
    return imports_section + f"// prettier-ignore\nexport type {classname} = {extends}{{\n{os.linesep.join(ts_properties)}\n}}"




def convert_java_type_to_ts_type(java_type):
    java_type = java_type.strip()

    if java_type in ['int[]', 'Integer[]', 'long[]', 'Long[]', 'float[]', 'Float[]', 'double[]', 'Double[]', 'short[]', 'Short[]', 'byte[]', 'Byte[]']:
        return 'number[]'
    elif java_type in ['boolean[]', 'Boolean[]']:
        return 'boolean[]'
    elif java_type in ['String[]', 'Date[]']:
        return 'string[]'
    elif java_type in ['int', 'Integer', 'long', 'Long', 'float', 'Float', 'double', 'Double', 'short', 'Short', 'byte', 'Byte']:
        return 'number'
    elif java_type in ['boolean', 'Boolean']:
        return 'boolean'
    elif java_type in ['String', 'Date', 'static', 'Timestamp']:
        return 'string'
    elif java_type in ['MultipartFile', 'java.sql.Timestamp', 'Object', 'TreeNode<K,T>','TreeNodeDyna<K,T>', 'K', 'T']:
        return 'any'
    elif java_type in ['MultipartFile[]', 'Object[]']:
        return ('any', 'any[]')
    elif '[]' in java_type:
        return (java_type.replace('[]',''), java_type) 
    elif 'List' in java_type:
        match = re.match(r'List<(.*)>', java_type)
        
        if match:
            inner_type = match.group(1)

            if inner_type in ['int', 'Integer', 'long', 'Long', 'float', 'Float', 'double', 'Double', 'short', 'Short', 'byte', 'Byte']:
                return 'number[]'
            elif inner_type in ['boolean', 'Boolean']:
                return 'boolean[]'
            elif inner_type in ['String', 'Date', 'static', 'Timestamp']:
                return 'string[]'
            elif inner_type in ['TreeNode<K,T>', 'TreeNodeDyna<K,T>', 'Object']:
                return 'any[]'
            # else:
            #     logging.info(inner_type)

            converted_type = f'{inner_type}[]'
            return (inner_type, converted_type) 
        else:
            # logging.info(java_type)
            if 'List<Map<String' in java_type:
                return ('any', 'any[]') 
    elif 'Set' in java_type:
        match = re.match(r'Set<(.*)>', java_type)
        
        if match:
            inner_type = match.group(1)

            if inner_type in ['int', 'Integer', 'long', 'Long', 'float', 'Float', 'double', 'Double', 'short', 'Short', 'byte', 'Byte']:
                return 'number[]'
            elif inner_type in ['boolean', 'Boolean']:
                return 'boolean[]'
            elif inner_type in ['String', 'Date', 'static', 'Timestamp']:
                return 'string[]'
            elif inner_type in ['TreeNode<K,T>', 'TreeNodeDyna<K,T>', 'Object']: 
                return 'any[]'

            converted_type = f'{inner_type}[]'
            return (inner_type, converted_type) 
    # else:
    #     logging.info(java_type)

    return (java_type, java_type)  # use original java type name if not matched with any known types 






def get_comment(line):
    comment_match = re.search(r'//(.+)', line)
    return comment_match.group(1).strip() if comment_match else "" 