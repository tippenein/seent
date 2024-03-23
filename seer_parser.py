import re

def degen_color(emoji):
    if emoji:
        # Convert the Unicode emoji to the color name
        if emoji == '🔴':
            return 'red'
        elif emoji == '🟡':
            return 'yellow'
        elif emoji == '🟢':
            return 'green'
        else:
            return 'unknown'  # Default case if the emoji is not recognized
    else:
        return None

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
    ai_degen_pattern = re.compile(r'AI Degen: (\S+)')
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

    ai_degen_match = ai_degen_pattern.search(raw_text)
    data['ai_degen'] = degen_color(ai_degen_match.group(1)) if ai_degen_match else None
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