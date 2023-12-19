import unittest
from contract import Call, Put


class TestCall(unittest.TestCase):
    def setUp(self):
        self.option = Call(
            s_0=300,
            strike=250,
            maturity=1,
            risk_free_rate=0.03,
            volatility=0.15,
            actual_premium=50,
        )

    def test_call_bsm_price(self):
        expected_price = 58.82
        self.assertEqual(round(self.option.bsm_price, 2), expected_price)

    def test_post_init(self):
        with self.assertRaises(Exception):
            Call(
                s_0=100,
                strike=100,
                maturity=1,
                risk_free_rate=0.05,
                volatility=0.2,
                product="invalid_product",
            )

    def test_call_delta(self):
        expected_delta = 0.932
        self.assertEqual(round(self.option.delta, 3), expected_delta)

    def test_call_gamma(self):
        expected_gamma = 0.003
        self.assertEqual(round(self.option.gamma, 3), expected_gamma)


class TestPut(unittest.TestCase):
    def setUp(self):
        self.option = Put(
            s_0=300,
            strike=250,
            maturity=1,
            risk_free_rate=0.03,
            volatility=0.15,
            actual_premium=50,
        )

    def test_put_bsm_price(self):
        expected_price = 1.43
        self.assertEqual(round(self.option.bsm_price, 2), expected_price)

    def test_post_init(self):
        with self.assertRaises(Exception):
            Put(
                s_0=100,
                strike=100,
                maturity=1,
                risk_free_rate=0.05,
                volatility=0.2,
                product="invalid_product",
            )


if __name__ == "__main__":
    unittest.main()
