import json

import requests
import sys

# Main loop simplified for clarity
if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else None
    url = "http://127.0.0.1:8000/query/"

    while True:
        user_input = input("Prompt: ") if not query else query
        if user_input.lower() in ['quit', 'q', 'exit']:
            sys.exit()


        # Sending a POST request with the JSON payload
        response = requests.get(f"{url}{user_input}")

        if response.status_code == 200:
            # Parse the JSON response and then pretty-print it
            response_json = response.json()
            # Access and print the desired information
            print(response_json)
        else:
            print(f"Error: {response.status_code} - {response.text}")

            # Reset query to None for the loop to continue with user inputs
        query = None