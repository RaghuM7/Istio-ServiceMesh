import json
import yaml
from collections import Counter

def filter_valid_json(lines):
    valid_json_lines = []
    buffer = ""
    for line in lines:
        line = line.strip()
        buffer += line
        try:
            json_object = json.loads(buffer)
            valid_json_lines.append(buffer)
            buffer = ""
        except json.JSONDecodeError:
            pass
    return valid_json_lines

def main():
    # Read the input file and filter out lines containing complete JSON objects
    with open('/root/logs.txt', 'r') as file:
        lines = file.readlines()
        valid_json_lines = filter_valid_json(lines)

    # Write the valid JSON lines to a new file
    with open('/root/output_file.txt', 'w') as file:
        file.write('\n'.join(valid_json_lines))

    # Read the contents of the text file
    with open('/root/output_file.txt', 'r') as file:
        data = file.readlines()

    # Remove leading/trailing whitespace and newline characters
    data = [line.strip() for line in data]

    # Combine JSON objects into a single string separated by ','
    json_array = '[' + ','.join(data) + ']'

    # Write the modified JSON array to a new file
    with open('/root/logs.json', 'w') as file:
        file.write(json_array)

    # Open the file containing the JSON array
    with open('/root/logs.json', 'r') as file:
        # Load JSON data
        logs = json.load(file)

        # Open a file to write request IDs
        with open('/root/request_ids.txt', 'w') as output_file:
            # Iterate over each log entry
            for log in logs:
                # Extract request_id
                request_id = log.get('request_id')

                # Write request_id to the output file
                output_file.write(str(request_id) + '\n')

    # Read request_ids.txt to get request IDs
    with open('/root/request_ids.txt', 'r') as file:
        request_ids = file.read().splitlines()

    # Count occurrences of each request ID
    request_id_counts = Counter(request_ids)

    # Extract request IDs repeated >= 3 times
    repeated_request_ids = [request_id for request_id, count in request_id_counts.items() if count >= 3]

    # Generate VirtualService YAML for repeated request IDs
    virtual_service_yaml = []

    for request_id in repeated_request_ids:
        virtual_service_yaml.append({
            'apiVersion': 'networking.istio.io/v1alpha3',
            'kind': 'VirtualService',
            'metadata': {
                'name': f'reviews-{request_id}-vs'
            },
            'spec': {
                'hosts': ['reviews'],
                'http': [
                    {
                        'match': [
                            {
                                'headers': {
                                    'end-user': {
                                        'exact': request_id
                                    }
                                }
                            }
                        ],
                        'route': [
                            {
                                'destination': {
                                    'host': 'reviews',
                                    'subset': 'v2'
                                }
                            }
                        ]
                    },
                    {
                        'route': [
                            {
                                'destination': {
                                    'host': 'reviews',
                                    'subset': 'v1'
                                }
                            }
                        ]
                    }
                ]
            }
        })

    # Write VirtualService YAML to a file
    with open('/root/virtual_services.yaml', 'w') as yaml_file:
        yaml.dump_all(virtual_service_yaml, yaml_file, default_flow_style=False)

if __name__ == "__main__":
    main()


