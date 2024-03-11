import unittest
from seer_parser import parse_token_data

# Test case class
class TestTokenDataParsing(unittest.TestCase):
    def setUp(self):
        self.text = """
        Address: EBrMAYymNrAkgmmEkeZ23dhKe6oAT5ZwMXPPMEFDSDUp

        Pair: THPS2/SOL

        🏦Financials🏦
        Price: $7.38e-06
        Latest Marketcap: $6.20k
        Transactions: 0
        Price Change: -0.12%
        Volume: $307.61k

        📊Ratings📊
        Memeability: 9.9/10
        AI Degen: 🔴 - Red

        🔒Security🔒
        Top 20 Holders: 75.8%
        Total Holders: 133
        """


    def test_parsing(self):
        data = parse_token_data(self.text)
        self.assertEqual(data['token'], "EBrMAYymNrAkgmmEkeZ23dhKe6oAT5ZwMXPPMEFDSDUp")
        self.assertEqual(data['marketcap'], 6200)
        self.assertEqual(data['price_change'], -0.12)
        self.assertEqual(data['volume'], 307610)
        self.assertEqual(data['top_20_holders'], 75.8)
        self.assertEqual(data['total_holders'], 133)

    def test_name(self):
        data = parse_token_data(self.text)
        self.assertEqual(data['name'], "THPS2/SOL")

    def test_price(self):
        data = parse_token_data(self.text)
        self.assertEqual(data['price'], 7.38e-06)

    def test_meme(self):
        data = parse_token_data(self.text)
        self.assertEqual(data['memeability'], 9.9)

    def test_ai_degen(self):
        data = parse_token_data(self.text)
        self.assertEqual(data['ai_degen'], 'red')

    # Add more test methods for each piece of data...

# Run the tests
if __name__ == '__main__':
    unittest.main()