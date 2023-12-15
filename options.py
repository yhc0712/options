import numpy as np
from scipy.stats import norm

def BlackScholes(S, K, T, r, Sigma, OptionType):
    
    d1 = (np.log(S/K) + (r + 0.5 * Sigma**2) * T) / (Sigma * np.sqrt(T))
    d2 = d1 - Sigma * np.sqrt(T)

    if OptionType == 'Call':
        cp_coefficient = 1
    elif OptionType == 'Put':
        cp_coefficient = -1
    else:
        print('Error: OptionType must be Call or Put.')
        return 0

    premium = cp_coefficient * (S * norm.cdf(d1 * cp_coefficient) - K * np.exp(-r * T) * norm.cdf(d2 * cp_coefficient))

    return premium

def delta(S, K, T, r, Sigma, OptionType):
        
        d1 = (np.log(S/K) + (r + 0.5 * Sigma**2) * T) / (Sigma * np.sqrt(T))
        N_d1 = norm.cdf(d1)

        if OptionType == 'Call':
            return N_d1
        elif OptionType == 'Put':
            return N_d1 - 1
        else:
            print('Error: OptionType must be Call or Put.')
            return 0
        
def gamma(percent, S, K, T, r, Sigma, OptionType):
    gamma_up = delta(S * (1 + percent / 100), K, T, r, Sigma, OptionType) - delta(S, K, T, r, Sigma, OptionType)
    gamma_down = delta(S * (1 - percent / 100), K, T, r, Sigma, OptionType) - delta(S, K, T, r, Sigma, OptionType)
    return (gamma_up - gamma_down) / 2.

def theta_one_day(S, K, T, r, Sigma, OptionType):
    return BlackScholes(S, K, T - 1/252, r, Sigma, OptionType) - BlackScholes(S, K, T, r, Sigma, OptionType)

def vega_one_percent(S, K, T, r, Sigma, OptionType):
    return BlackScholes(S, K, T, r, Sigma + 0.01, OptionType) - BlackScholes(S, K, T, r, Sigma, OptionType)



class Option():

    def __init__(self, Prod, S, K, T, r, Sigma, Position):
        self.Prod = Prod
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.Sigma = Sigma
        self.Position = Position
        self.Multiplier = 50
        self.cash_coefficient = self.Multiplier * Position

    def update_greeks(self, S_sim):
        self.S_sim = S_sim
        self.bsm_price = BlackScholes(self.S_sim, self.K, self.T, self.r, self.Sigma, self.Prod) * self.cash_coefficient
        self.cash_delta = delta(self.S_sim, self.K, self.T, self.r, self.Sigma, self.Prod) * self.cash_coefficient
        self.cash_gamma = gamma(1, self.S_sim, self.K, self.T, self.r, self.Sigma, self.Prod) * self.cash_coefficient
        self.theta = theta_one_day(self.S_sim, self.K, self.T, self.r, self.Sigma, self.Prod) * self.cash_coefficient
        self.vega = vega_one_percent(self.S_sim, self.K, self.T, self.r, self.Sigma, self.Prod) * self.cash_coefficient
        self.pnl = (BlackScholes(self.S_sim, self.K, self.T, self.r, self.Sigma, self.Prod) - BlackScholes(self.S, self.K, self.T, self.r, self.Sigma, self.Prod)) * self.cash_coefficient
    