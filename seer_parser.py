import re

def get_max_degen(degen_dict):
    # Filter out None values
    filtered_dict = {k: v for k, v in degen_dict.items() if v is not None}
    if not filtered_dict:
        # Return None or a default value if all values were None
        return None
    # Find the key with the maximum value
    max_key = max(filtered_dict, key=filtered_dict.get)
    return max_key


def parse_marketcap(marketcap_str):
    # This function converts a marketcap string like "$6.20k" to a float value
    suffixes = {'k': 1e3, 'm': 1e6, 'b': 1e9}
    if marketcap_str[-1].lower() in suffixes:
        # Extract the numeric part and the suffix
        number, suffix = marketcap_str[:-1], marketcap_str[-1].lower()
        # Convert to float and multiply by the corresponding factor
        return float(number) * suffixes[suffix]
    else:
        # If there's no suffix, just convert to float
        return float(marketcap_str)

def parse_volume(volume_str):
    suffixes = {'k': 1e3, 'm': 1e6, 'b': 1e9}
    if volume_str[-1].isdigit():  # No suffix
        return float(volume_str)
    else:  # There is a suffix
        number, suffix = volume_str[:-1], volume_str[-1].lower()
        return float(number) * suffixes.get(suffix, 1)

def parse_token_data(raw_text):
    data = {}
    token_pattern = re.compile(r'Address: ([-\w.]+)')
    name_pattern = re.compile(r'Name: (.+)', re.UNICODE)

    price_pattern = re.compile(r'Price: \$(\S+)')
    memeability_pattern = re.compile(r'Memeability: ([\d.]+)/10')
    top_holders_pattern = re.compile(r'Top 20 Holders: ([\d.]+)')
    total_holders_pattern = re.compile(r'Total Holders: (\d+)')
    transactions_pattern = re.compile(r'Transactions: (\d+)')
    version_pattern = re.compile(r'Seer ([-\$\w./]+)')


    volume_pattern = re.compile(r'Volume: \$([\d.]+[kMB]?)')
    volume_match = volume_pattern.search(raw_text)
    if volume_match:
        data['volume'] = parse_volume(volume_match.group(1))
    else:
        data['volume'] = None

    marketcap_pattern = re.compile(r'Latest Marketcap: \$([\d.]+[kMB]?)')
    marketcap_match = marketcap_pattern.search(raw_text)
    if marketcap_match:
        data['marketcap'] = parse_marketcap(marketcap_match.group(1))
    else:
        data['marketcap'] = None
    liquidity_pattern = re.compile(r'Liquidity: \$([\d.]+[kMB]?)')
    liquidity_match = liquidity_pattern.search(raw_text)
    if liquidity_match:
        data['liquidity'] = parse_marketcap(liquidity_match.group(1))
    else:
        data['liquidity'] = None

    memeability_match = memeability_pattern.search(raw_text)
    if memeability_match:
        data['memeability'] = float(memeability_match.group(1))
    else:
        data['memeability'] = None

    name_originality_pattern = re.compile(r'Name Originality: ([\d.]+)/10')
    name_originality_match = name_originality_pattern.search(raw_text)
    if name_originality_match:
        data['name_originality'] = float(name_originality_match.group(1))
    else:
        data['name_originality'] = None
    description_originality_pattern = re.compile(r'Description Originality: ([\d.]+)/10')
    description_originality_match = description_originality_pattern.search(raw_text)
    if description_originality_match:
        data['description_originality'] = float(description_originality_match.group(1))
    else:
        data['description_originality'] = None

    # AI DEGEN
    ai_degen_death_pattern = re.compile(r'.*Death ([\d.]+)\%')
    ai_degen_red_pattern = re.compile(r'.*Red ([\d.]+)\%')
    ai_degen_yellow_pattern = re.compile(r'.*Yellow ([\d.]+)\%')
    ai_degen_green_pattern = re.compile(r'.*Green ([\d.]+)\%')

    ai_degen_death_match = ai_degen_death_pattern.search(raw_text)
    ai_degen_death = float(ai_degen_death_match.group(1)) if ai_degen_death_match else None
    data['ai_degen_death'] = ai_degen_death
    ai_degen_green_match = ai_degen_green_pattern.search(raw_text)
    ai_degen_green = float(ai_degen_green_match.group(1)) if ai_degen_green_match else None
    data['ai_degen_green'] = ai_degen_green
    ai_degen_yellow_match = ai_degen_yellow_pattern.search(raw_text)
    ai_degen_yellow = float(ai_degen_yellow_match.group(1)) if ai_degen_yellow_match else None
    data['ai_degen_yellow'] = ai_degen_yellow
    ai_degen_red_match = ai_degen_red_pattern.search(raw_text)
    ai_degen_red = float(ai_degen_red_match.group(1)) if ai_degen_red_match else None
    print(ai_degen_death, ai_degen_green, ai_degen_yellow, ai_degen_red)
    data['ai_degen_red'] = ai_degen_red
    data['ai_degen'] = get_max_degen({'death': ai_degen_death,
       'red': ai_degen_red,
       'yellow': ai_degen_yellow,
       'green': ai_degen_green
      })
    # Search for matches in the raw text
    token_match = token_pattern.search(raw_text)
    data['token'] = token_match.group(1) if token_match else None

    name_match = name_pattern.search(raw_text)
    data['name'] = name_match.group(1) if name_match else None

    price_match = price_pattern.search(raw_text)
    data['price'] = float(price_match.group(1)) if price_match else None

    top_20_holders_match = top_holders_pattern.search(raw_text)
    data['top_20_holders'] = float(top_20_holders_match.group(1)) if top_20_holders_match else 0.0

    total_holders_match = total_holders_pattern.search(raw_text)
    data['total_holders'] = int(total_holders_match.group(1)) if total_holders_match else 0

    transactions_match = transactions_pattern.search(raw_text)
    data['transactions'] = int(transactions_match.group(1)) if transactions_match else 0

    price_change_pattern = re.compile(r'5m Price Change: ([-\d.]+)%')
    price_change_5min_match = price_change_pattern.search(raw_text)
    data['price_change_5min'] = float(price_change_5min_match.group(1)) if price_change_5min_match else 0.0

    version_match = version_pattern.search(raw_text)
    if version_match:
        data['version'] = version_match.group(1)
    else:
        data['version'] = None


    return data
