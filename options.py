import numpy as np
from scipy.stats import norm
from dataclasses import dataclass


def BlackScholes(S, K, T, r, Sigma, OptionType):
    d1 = (np.log(S / K) + (r + 0.5 * Sigma**2) * T) / (Sigma * np.sqrt(T))
    d2 = d1 - Sigma * np.sqrt(T)

    if OptionType == "call":
        cp_coefficient = 1
    elif OptionType == "put":
        cp_coefficient = -1
    else:
        print(OptionType)
        raise Exception("Error: OptionType must be Call or Put.")

    premium = cp_coefficient * (
        S * norm.cdf(d1 * cp_coefficient)
        - K * np.exp(-r * T) * norm.cdf(d2 * cp_coefficient)
    )

    return premium


def delta(S, K, T, r, Sigma, OptionType):
    d1 = (np.log(S / K) + (r + 0.5 * Sigma**2) * T) / (Sigma * np.sqrt(T))
    N_d1 = norm.cdf(d1)

    if OptionType == "call":
        return N_d1
    elif OptionType == "put":
        return N_d1 - 1
    else:
        raise Exception("Error: OptionType must be Call or Put.")


def gamma(percent, S, K, T, r, Sigma, OptionType):
    gamma_up = delta(S * (1 + percent / 100), K, T, r, Sigma, OptionType) - delta(
        S, K, T, r, Sigma, OptionType
    )
    gamma_down = delta(S * (1 - percent / 100), K, T, r, Sigma, OptionType) - delta(
        S, K, T, r, Sigma, OptionType
    )
    return (gamma_up - gamma_down) / 2.0


def theta_one_day(S, K, T, r, Sigma, OptionType):
    return BlackScholes(S, K, T - 1 / 252, r, Sigma, OptionType) - BlackScholes(
        S, K, T, r, Sigma, OptionType
    )


def vega_one_percent(S, K, T, r, Sigma, OptionType):
    return BlackScholes(S, K, T, r, Sigma + 0.01, OptionType) - BlackScholes(
        S, K, T, r, Sigma, OptionType
    )


@dataclass
class Option:
    Prod: str
    Original_Spot: float
    K: float
    T: float
    r: float
    Sigma: float
    Position: int
    _Multiplier: int = 50

    @property
    def _cash_coefficient(self):
        return self._Multiplier * self.Position

    @property
    def Spot_sim(self):
        return self._Spot_sim

    @Spot_sim.setter
    def Spot_sim(self, value):
        self._Spot_sim = value
        self.update_greeks()

    def update_greeks(self):
        self.bsm_price = BlackScholes(
            self.Spot_sim, self.K, self.T, self.r, self.Sigma, self.Prod
        )
        self.cash_delta = (
            delta(self.Spot_sim, self.K, self.T, self.r, self.Sigma, self.Prod)
            * self._cash_coefficient
        )
        self.cash_gamma = (
            gamma(1, self.Spot_sim, self.K, self.T, self.r, self.Sigma, self.Prod)
            * self._cash_coefficient
        )
        self.theta = (
            theta_one_day(self.Spot_sim, self.K, self.T, self.r, self.Sigma, self.Prod)
            * self._cash_coefficient
        )
        self.vega = (
            vega_one_percent(
                self.Spot_sim, self.K, self.T, self.r, self.Sigma, self.Prod
            )
            * self._cash_coefficient
        )
        self.pnl = (
            BlackScholes(self.Spot_sim, self.K, self.T, self.r, self.Sigma, self.Prod)
            - BlackScholes(
                self.Original_Spot, self.K, self.T, self.r, self.Sigma, self.Prod
            )
        ) * self._cash_coefficient
