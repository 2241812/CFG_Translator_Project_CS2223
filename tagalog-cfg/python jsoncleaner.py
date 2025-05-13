import json
import os

def remove_duplicate_json_entries(filepath):
    """
    Reads a JSON file (assuming it's a dictionary), removes duplicate
    key-value entries (keeping the first occurrence of each key), and
    overwrites the original file.
    This function is suitable for JSON files containing a top-level dictionary.

    Args:
        filepath (str): The path to the JSON file to process.
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        return

    try:
        # Read the JSON file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Ensure the loaded data is a dictionary
        if not isinstance(data, dict):
            print(f"Error: JSON file '{filepath}' does not contain a top-level dictionary.")
            print("This script is designed for JSON dictionaries (key-value pairs).")
            return

        # Create a new dictionary to store unique entries, preserving order
        # and keeping the first occurrence of each key.
        cleaned_data = {}
        for key, value in data.items():
            if key not in cleaned_data:
                cleaned_data[key] = value

        # Overwrite the original file with the cleaned data
        with open(filepath, 'w', encoding='utf-8') as f:
            # Use json.dump with indent for readability and ensure_ascii=False
            # to handle non-ASCII characters correctly.
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

        print(f"Successfully removed duplicate entries from '{filepath}'.")

    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{filepath}': {e}")
        print("Please ensure the file is valid JSON format.")
    except IOError as e:
        print(f"Error accessing file '{filepath}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

remove_duplicate_json_entries('tagalog_english_dict.json')
# remove_duplicate_json_entries('another_json_file.json') # Example for another JSON file
