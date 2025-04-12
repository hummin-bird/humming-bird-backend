import re
import json
import os
from pathlib import Path

def substitute_in_json_file(input_file_path, output_file_path, substitutions):
    """
    Substitute keywords in a JSON file using regular expressions.
    
    Args:
        input_file_path (str): Path to the input JSON file
        output_file_path (str): Path to save the modified JSON file
        substitutions (dict): Dictionary mapping regex patterns to replacement strings
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the input file
        with open(input_file_path, 'r') as file:
            content = file.read()
        
        # Apply each substitution
        for pattern, replacement in substitutions.items():
            content = re.sub(pattern, replacement, content)
        
        # Write the modified content to the output file
        with open(output_file_path, 'w') as file:
            file.write(content)
        
        return True
    
    except Exception as e:
        print(f"Error substituting in JSON file: {e}")
        return False

def substitute_in_json_object(json_obj, substitutions):
    """
    Substitute keywords in a JSON object using regular expressions.
    
    Args:
        json_obj (dict or list): The JSON object to modify
        substitutions (dict): Dictionary mapping regex patterns to replacement strings
    
    Returns:
        dict or list: The modified JSON object
    """
    # Convert the JSON object to a string
    json_str = json.dumps(json_obj)
    
    # Apply each substitution
    for pattern, replacement in substitutions.items():
        json_str = re.sub(pattern, replacement, json_str)
    
    # Convert back to a JSON object
    return json.loads(json_str)

# Example usage
if __name__ == "__main__":
    # Example substitutions
    substitutions = {
        r'\$QUERY': 'Build a mobile app for fitness tracking',
        r'\$product_type': 'mobileApp',
        r'plan-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}': 'plan-custom-id-12345'
    }
    
    # Example file paths
    input_file = "initiation_plan.json"
    output_file = "modified_plan.json"
    
    # Substitute in the file
    success = substitute_in_json_file(input_file, output_file, substitutions)
    
    if success:
        print(f"Successfully substituted keywords in {input_file} and saved to {output_file}")
    else:
        print("Failed to substitute keywords in the JSON file") 