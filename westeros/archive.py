import sys
import os
import json
import time

# Constants for maximum limits and page size
PAGE_SIZE = 10
MAX_FIELDS = 10
MAX_TYPE_NAME_LENGTH = 12
MAX_FIELD_NAME_LENGTH = 20

# Function to get the current timestamp
def get_timestamp():
    return int(time.time())

# Function to log an operation 
def log_operation(log_entries, timestamp, operation, status):
    log_entries.append(f"{timestamp}, {operation}, {status}")

# Function to create a new type
def create_type(type_name, num_fields, primary_key_order, fields):
    # Check if type already exists
    if os.path.exists(f"{type_name}.json"):
        return "failure"
    # Check if the type name exceeds the maximum allowed length
    if len(type_name) > MAX_TYPE_NAME_LENGTH:
        return "failure"
    # Check if the number of fields exceeds the maximum allowed limit
    if len(fields) // 2 > MAX_FIELDS:
        return "failure"
    # Check if any field name exceeds the maximum length
    if any(len(field) > MAX_FIELD_NAME_LENGTH for field in fields[::2]):
        return "failure"
    
    # Type metadata that will be stored in the JSON file
    type_metadata = {
        "type_name": type_name,
        "num_fields": num_fields,
        "primary_key_order": (primary_key_order-1), # Adjust primary_key_order to be zero-based index
        "fields": fields,
        "pages": []
    }
    
    # Create the JSON file for the new type
    with open(f"{type_name}.json", 'w') as file:
        json.dump(type_metadata, file)
    
    return "success"

# Function to create a new record
def create_record(type_name, record_values):
    file_path = f"{type_name}.json"
    # Check if the type file exists
    if not os.path.exists(file_path):
        return "failure"
    
    # Read the type metadata from the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Calculate the index of the primary key field
    primary_key_field_index = data['primary_key_order'] * 2 
    primary_key_field = data['fields'][primary_key_field_index]
    
    # Check for existing primary key
    for page in data['pages']:
        for record in page['records']:
            if record[primary_key_field] == record_values[data['primary_key_order']]:
                return "failure"
    
    pages = data['pages']
    
    # Add the record to the last page if it has space, otherwise create a new page
    if pages and len(pages[-1]['records']) < PAGE_SIZE:
        page = pages[-1]
    else:
        page = {"page_number": len(pages), "records": []}
        pages.append(page)
    # Create a new record dictionary
    record = {field: value for field, value in zip(data['fields'][0::2], record_values)}
    page['records'].append(record)
    
    # Write the updated data back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(data, file)
    
    return "success"

# Function to delete a record
def delete_record(type_name, primary_key):
    file_path = f"{type_name}.json"
    # Check if the type file exists
    if not os.path.exists(file_path):
        return "failure"
    
    # Read the type metadata from the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Calculate the index of the primary key field
    primary_key_field_index = data['primary_key_order'] * 2
    primary_key_field = data['fields'][primary_key_field_index]
    
    pages = data['pages']
    
    # Search for the record with the given primary key and delete it
    for page in pages:
        for record in page['records']:
            if record[primary_key_field] == primary_key:
                page['records'].remove(record)
                # If the page becomes empty after deleting the record, remove the page
                if not page['records']:
                    pages.remove(page)
                # Write the updated data back to the JSON file
                with open(file_path, 'w') as file:
                    json.dump(data, file)
                return "success"
    
    return "failure"

# Function to search for a record
def search_record(type_name, primary_key):
    file_path = f"{type_name}.json"
    # Check if the type file exists
    if not os.path.exists(file_path):
        return "failure"
    
    # Read the type metadata from the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Calculate the index of the primary key field
    primary_key_field_index = data['primary_key_order'] * 2
    primary_key_field = data['fields'][primary_key_field_index]
    
    pages = data['pages']
    
    # Search for the record with the given primary key and return it
    for page in pages:
        for record in page['records']:
            if record[primary_key_field] == primary_key:
                return " ".join([str(record[field]) for field in data['fields'][0::2]])
    
    return "failure"

# Function to process the input file and generate the output and log files
def process_input_file(input_file_path, output_file_path, log_file_path):
    with open(input_file_path, 'r') as file:
        lines = file.readlines()
    
    # Lists to store the output entries and log entries
    output_entries = []
    log_entries = []

    # Process each line in the input file
    for line in lines:
        parts = line.strip().split() # Split the line into words
        operation = parts[0] # Operation is the first word in the line
        timestamp = get_timestamp() # Get the current timestamp
        
        # Process the operation based on the operation type
        if operation == "create":
            sub_operation = parts[1] # Sub-operation is the second word in the line
            if sub_operation == "type":
                type_name = parts[2]
                num_fields = int(parts[3])
                primary_key_order = int(parts[4])
                fields = parts[5:]
                result = create_type(type_name, num_fields, primary_key_order, fields) # Call create_type function
                log_operation(log_entries, timestamp, line.strip(), result) # Log the operation
            elif sub_operation == "record":
                type_name = parts[2]
                record_values = parts[3:]
                result = create_record(type_name, record_values) # Call create_record function
                log_operation(log_entries, timestamp, line.strip(), result) # Log the operation
        elif operation == "delete":
            type_name = parts[2]
            primary_key = parts[3]
            result = delete_record(type_name, primary_key) # Call delete_record function
            log_operation(log_entries, timestamp, line.strip(), result) # Log the operation
        elif operation == "search":
            type_name = parts[2]
            primary_key = parts[3]
            result = search_record(type_name, primary_key) # Call search_record function

            # Log the operation and add the result to the output entries if it is a success
            if result == "failure":
                log_operation(log_entries, timestamp, line.strip(), result)
            else:
                log_operation(log_entries, timestamp, line.strip(), "success")
                output_entries.append(result)
    
    # Write the output entries to the output file
    with open(output_file_path, 'w') as file:
        for entry in output_entries:
            file.write(entry + "\n")
    
    # Open log file in append mode to preserve old log entries
    with open(log_file_path, 'a') as file:
        for entry in log_entries:
            file.write(entry + "\n")

if __name__ == "__main__":
    # Check if the input file path is provided as a command line argument
    if len(sys.argv) != 2:
        print("Usage: python3 2020400255/archive.py <input_file_path>")
        sys.exit(1)
    
    # Call the process_input_file function with the input file path and default output and log file paths
    input_file_path = sys.argv[1]
    output_file_path = "output.txt"
    log_file_path = "log.csv"
    
    # Call the process_input_file function
    process_input_file(input_file_path, output_file_path, log_file_path)