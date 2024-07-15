import json
import xmltodict
import os

def xml_to_json_txt(xml_file):
    try:
        # Read the XML file
        with open(xml_file, 'r') as file:
            xml_data = file.read()

        # Parse XML to OrderedDict
        xml_dict = xmltodict.parse(xml_data)

        # Convert OrderedDict to JSON
        json_data = json.dumps(xml_dict, indent=4)

        # Generate TXT file name and path
        xml_dir = os.path.dirname(xml_file)
        xml_filename = os.path.basename(xml_file)
        txt_filename = os.path.splitext(xml_filename)[0] + '_direct_json.txt'
        txt_file_path = os.path.join(xml_dir, txt_filename)

        # Write JSON content to a new TXT file
        with open(txt_file_path, 'w') as file:
            file.write(json_data)

        print(f"Conversion complete. TXT file with JSON content created at {txt_file_path}")
        return txt_file_path

    except Exception as e:
        print(f"Error processing XML file {xml_file}: {str(e)}")
        return None

# Usage
xml_file_path = "parts.xml"
txt_file = xml_to_json_txt(xml_file_path)
# if txt_file:
#     print(f"Conversion complete. TXT file created at {txt_file}")