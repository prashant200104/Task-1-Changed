import os
from unstructured.partition.xml import partition_xml
from unstructured.staging.base import convert_to_dict
from unstructured.cleaners.core import (
    clean, clean_bullets, clean_extra_whitespace,
    clean_dashes, clean_trailing_punctuation,
    group_broken_paragraphs, replace_unicode_quotes
)
import json
from bs4 import BeautifulSoup

def process_xml_to_json_txt(xml_file_path):
    def filter_xml(xml_content, tags_to_remove):
        soup = BeautifulSoup(xml_content, 'xml')
        for tag in tags_to_remove:
            for element in soup.find_all(tag):
                element.decompose()
        return str(soup)

    def clean_text(text):
        text = clean(text, bullets=True, extra_whitespace=True, dashes=True, trailing_punctuation=True)
        text = clean_bullets(text)
        text = clean_extra_whitespace(text)
        text = clean_dashes(text)
        text = clean_trailing_punctuation(text)
        text = replace_unicode_quotes(text)
        text = group_broken_paragraphs(text)
        return text

    def process_element(element):
        if isinstance(element, dict):
            return {k: process_element(v) for k, v in element.items()}
        elif isinstance(element, list):
            return [process_element(item) for item in element]
        elif isinstance(element, str):
            return clean_text(element)
        else:
            return element

    def process_metadata(element):
        if isinstance(element, dict) and 'metadata' in element:
            metadata = element['metadata']
            metadata.pop('file_directory', None)
            metadata.pop('last_modified', None)
        return process_element(element)

    # Read the XML file
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    # Filter out unwanted tags (if any)
    tags_to_remove = []  # Add tags to remove if needed
    filtered_xml = filter_xml(xml_content, tags_to_remove)

    # Partition the filtered XML
    elements = partition_xml(text=filtered_xml)

    # Convert the elements to a dictionary, process metadata, and clean text
    data_dict = convert_to_dict(elements)
    data_dict = [process_metadata(element) for element in data_dict]

    # Convert the dictionary to JSON
    json_data = json.dumps(data_dict, indent=2)

    # Create "cleaned data" folder
    xml_dir = os.path.dirname(xml_file_path)
    cleaned_data_dir = os.path.join(xml_dir, "data")
    os.makedirs(cleaned_data_dir, exist_ok=True)

    # Create TXT file path in the "cleaned data" folder
    xml_filename = os.path.basename(xml_file_path)
    txt_filename = os.path.splitext(xml_filename)[0] + '_cleaned_json.txt'
    txt_file_path = os.path.join(cleaned_data_dir, txt_filename)

    # Save JSON content to TXT file
    try:
        with open(txt_file_path, "w", encoding='utf-8') as f:
            f.write(json_data)
        print(f"Processed XML file: {xml_file_path}")
        print(f"Created TXT file with cleaned JSON content: {txt_file_path}")
    except Exception as e:
        print(f"Error saving to TXT file: {str(e)}")

    return txt_file_path

# Example usage
# xml_file_path = "parts.xml"
# txt_file_path = process_xml_to_txt(xml_file_path)