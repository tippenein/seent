import unittest
from seer_parser import parse_token_data

# Test case class
class TestTokenDataParsing(unittest.TestCase):
    def setUp(self):
        self.text = """
        Address: B45QLZLZNwHo5ya5TQdjkE6A4xLCvNYvcRtjvFFZ9T72

        Name: doege

        📊Ratings📊
        Memeability: 9.4/10
        AI Degen:
        ☠️ - Death 10.12%
        🔴 - Red 82.23%
        🟡 - Yellow 12.12%
        🟢 - Green 0.02%
        Name Originality: 5.8/10
        Description Originality: 10/10

        🏦Financials🏦
        Price: $0.114
        Liquidity: $98.61k
        Latest Marketcap: $1.10M
        Transactions: 722
        5m Price Change: 20.54%
        Volume: $49.42k

        🔒Security🔒
        Top 20 Holders: 29.9%
        Total Holders: 3822

        Seer v1.35

        """

    def test_parsing(self):
        data = parse_token_data(self.text)
        self.assertEqual(data['token'], "B45QLZLZNwHo5ya5TQdjkE6A4xLCvNYvcRtjvFFZ9T72")
        self.assertEqual(data['marketcap'], 1100000)
        self.assertEqual(data['price_change_5min'], 20.54)
        self.assertEqual(data['volume'], 49420)
        self.assertEqual(data['name'], "doege")

    def test_security(self):
        data = parse_token_data(self.text)
        self.assertEqual(data['top_20_holders'], 29.9)
        self.assertEqual(data['total_holders'], 3822)

    def test_meme(self):
        data = parse_token_data(self.text)
        self.assertEqual(data['memeability'], 9.4)
        self.assertEqual(data['name_originality'], 5.8)
        self.assertEqual(data['description_originality'], 10.0)

        self.assertEqual(data['ai_degen_death'],  10.12)
        self.assertEqual(data['ai_degen_red'], 82.23)
        self.assertEqual(data['ai_degen_yellow'], 12.12)
        self.assertEqual(data['ai_degen_green'], 0.02)


    def test_millions(self):
        data = parse_token_data("Volume: $139.78M")
        self.assertEqual(data['volume'], 139780000)

    def test_version(self):
        data = parse_token_data(self.text)
        self.assertEqual(data['version'], 'v1.35')

    def test_emoji_name(self):
        data = parse_token_data("Name: 🦔 Sonik The Hedgehog AI")
        self.assertEqual(data['name'], "🦔 Sonik The Hedgehog AI")

if __name__ == '__main__':
    unittest.main()
