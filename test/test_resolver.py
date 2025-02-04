from unittest import TestCase

from libbtc1.resolver import parse_btc1_identifier

class ParseBtc1IdentifierTest(TestCase):

    def test_parse_btc1_identifier(self):
        tests = [
            {
                "did": "did:btc1:k1t5rm7vud58tyspensq9weyxc49cyxyvyh72w0n5hc7g5t859aq7sz45d5a",
                "identifier_components": {
                    "version": 1,
                    "network": "mainnet",
                    "hrp": "k",
                    "genesis_bytes": bytearray([
                        93, 7, 191, 51, 141, 161, 214, 72, 7, 51, 128, 10, 236,
                        144, 216, 169, 112, 67, 17, 132, 191, 148, 231, 206,
                        151, 199, 145, 69, 158, 133, 232, 61,
                    ])
                }
            }
        ]

        for test in tests:
            identifier_components = parse_btc1_identifier(test["did"])

            self.assertDictEqual(identifier_components, test["identifier_components"])