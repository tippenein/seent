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
    name_pattern = re.compile(r'Pair: ([-\$\w./]+)')
    price_pattern = re.compile(r'Price: \$(\S+)')
    marketcap_pattern = re.compile(r'Latest Marketcap: \$([\d.]+[kmb]?)')
    volume_pattern = re.compile(r'Volume 24h: ([\d.]+[kmb]?)')
    memeability_pattern = re.compile(r'Memeability: ([\d.]+)/10')
    ai_degen_pattern = re.compile(r'AI Degen: (\S+)')
    top_holders_pattern = re.compile(r'Top 20 Holders: ([\d.]+)')
    total_holders_pattern = re.compile(r'Total Holders: (\d+)')
    transactions_pattern = re.compile(r'Transactions: (\d+)')

    price_change_pattern = re.compile(r'Price Change: ([-\d.]+)%')
    price_change_match = price_change_pattern.search(raw_text)
    if price_change_match:
        data['price_change'] = float(price_change_match.group(1))
    else:
        data['price_change'] = None

    volume_pattern = re.compile(r'Volume: \$([\d.]+[kmb]?)')
    volume_match = volume_pattern.search(raw_text)
    if volume_match:
        data['volume'] = parse_volume(volume_match.group(1))
    else:
        data['volume'] = None

    marketcap_match = marketcap_pattern.search(raw_text)
    if marketcap_match:
        # Convert the marketcap string to a float value
        data['marketcap'] = parse_marketcap(marketcap_match.group(1))
    else:
        data['marketcap'] = None

    memeability_match = memeability_pattern.search(raw_text)
    if memeability_match:
        data['memeability'] = float(memeability_match.group(1))
    else:
        data['memeability'] = None

    volume_24h_match = volume_pattern.search(raw_text)
    data['volume_24h'] = volume_24h_match.group(1) if volume_24h_match else None

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

    price_change_5min_match = price_change_pattern.search(raw_text)
    data['price_change_5min'] = float(price_change_5min_match.group(1)) if price_change_5min_match else 0.0


    return data