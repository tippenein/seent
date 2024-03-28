import requests

def fetch_token_data(tokens):
    # Join the list of hashes into a single string separated by '%2C'
    hashes_str = '%2C'.join(tokens)

    # Construct the URL with the joined hashes string
    url = f"https://api.geckoterminal.com/api/v2/networks/solana/tokens/multi/{hashes_str}"

    # Make the GET request to the endpoint
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()['data']
        d = {}
        for t in data:
            hash = t['attributes']['address']
            d[hash] = t['attributes']
        return d
    else:
        # Handle errors (e.g., network issues, invalid hashes, etc.)
        print(f"Error fetching data: {response.status_code}")
        return None