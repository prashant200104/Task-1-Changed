import os
from xml.dom import minidom

def process_xml_to_txt(xml_file_path):
    try:
        # Read the XML file
        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()

        # Parse the XML content
        xml_dom = minidom.parseString(xml_content)

        # Pretty-print the XML
        pretty_xml = xml_dom.toprettyxml(indent="  ")

        # Create "data" folder
        xml_dir = os.path.dirname(xml_file_path)
        data_dir = os.path.join(xml_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        # Create output TXT file path in the "data" folder
        xml_filename = os.path.basename(xml_file_path)
        txt_filename = os.path.splitext(xml_filename)[0] + '.txt'
        txt_file_path = os.path.join(data_dir, txt_filename)

        # Save the pretty-printed XML to a TXT file in the "data" folder
        with open(txt_file_path, "w", encoding='utf-8') as f:
            f.write(pretty_xml)

        print(f"Converted XML file: {xml_file_path}")
        print(f"Created TXT file with XML content: {txt_file_path}")

        return txt_file_path

    except Exception as e:
        print(f"Error converting XML file {xml_file_path} to TXT: {str(e)}")
        return None

# # Example usage
# xml_file_path = "parts.xml"
# txt_file_path = process_xml_to_txt_file(xml_file_path)