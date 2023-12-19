import numpy as np
from scipy.stats import norm
from dataclasses import dataclass
from options import BlackScholes, delta, gamma, theta_one_day, vega_one_percent


@dataclass
class Contract:
    """
    參數
    ----
    product: str
        產品名稱，可以是 futures, call 或 put
    s_0: float
        新倉時標的物的現價。
        TODO 目前直接在建立物件時指定，之後可以改成從資料庫讀取
    strike: float
        履約價
    maturity: float
        到期日，以年為單位。
        TODO 目前直接在建立物件時指定，之後改成以建倉日為基準，從資料庫讀取到期日，再計算到期日距離建倉日的天數
    risk_free_rate: float
        無風險利率，以小數表示，例如 0.01 表示 1%
        TODO 目前直接在建立物件時指定，之後改成以建倉日為基準，從資料庫讀取無風險利率
    volatility: float
        波動度，以小數表示，例如 0.3 表示 30%
        TODO 目前直接在建立物件時指定，之後改成以建倉日為基準，從資料庫讀取波動度
    multiplier: float
        乘數，例如台指期貨的乘數是 200

    """

    strike: float
    product: str
    s_0: float = 17652.03
    maturity: float = 9 / 252
    risk_free_rate: float = 0.0158
    volatility: float = 0.1011
    multiplier: float = 1
    position: int = 1

    def __post_init__(self):
        # 驗證 product 的值是否為 tx、mtx、call 或 put
        if self.product not in ["tx", "mtx", "call", "put"]:
            raise Exception('Error: product must be "tx", "mtx", "call" or "put".')
        # auto-set value of multiplier based on product
        if self.product == "tx":
            self.multiplier = 200
        elif self.product in ["call", "put", "mtx"]:
            self.multiplier = 50
        else:
            raise Exception('Error: product must be "tx", "mtx", "call" or "put".')
        self._simulation_spot = self.s_0

    @property
    def delta(self):
        self._delta = delta(
            S=self._simulation_spot,
            K=self.strike,
            T=self.maturity,
            r=self.risk_free_rate,
            Sigma=self.volatility,
            OptionType=self.product,
        )
        return self._delta

    @property
    def gamma(self, percent=1):
        self._gamma = gamma(
            percent=percent,
            S=self._simulation_spot,
            K=self.strike,
            T=self.maturity,
            r=self.risk_free_rate,
            Sigma=self.volatility,
            OptionType=self.product,
        )
        return self._gamma

    @property
    def theta(self):
        self._theta = theta_one_day(
            S=self._simulation_spot,
            K=self.strike,
            T=self.maturity,
            r=self.risk_free_rate,
            Sigma=self.volatility,
            OptionType=self.product,
        )
        return self._theta

    @property
    def vega(self):
        self._vega = vega_one_percent(
            S=self._simulation_spot,
            K=self.strike,
            T=self.maturity,
            r=self.risk_free_rate,
            Sigma=self.volatility,
            OptionType=self.product,
        )
        return self._vega

    @property
    def simulation_spot(self):
        return self._simulation_spot

    @simulation_spot.setter
    def simulation_spot(self, s_t: float):
        self._simulation_spot = s_t
        # get new values of delta, gamma, theta based on new simulation spot
        self.delta
        self.gamma
        self.theta
        self.vega


@dataclass
class Futures(Contract):
    """
    TODO pending
    """

    pass


@dataclass
class TX(Futures):
    product: str = "tx"


@dataclass
class MTX(Futures):
    product: str = "mtx"


@dataclass
class Option(Contract):

    """
    契約 expiration_month: str
        到期月份，例如 2021/09 的到期月份是 202109
        「自交易當月起連續3個月份，另加上3月、6月、9月、12月中2個接續的季月，另除每月第1個星期三外，得於交易當週之星期三一般交易時段加掛次二週之星期三到期之契約。」

    """

    actual_premium: float = -1
    _bsm_price: float = 0
    # expiration_month: str

    # theoretical values of an option calculated based on the Black-Scholes-Merton model
    @property
    def bsm_price(self):
        self._bsm_price = BlackScholes(
            S=self.s_0,
            K=self.strike,
            T=self.maturity,
            r=self.risk_free_rate,
            Sigma=self.volatility,
            OptionType=self.product,
        )
        return self._bsm_price

    # @bsm_price.setter
    # def bsm_price(self, s_t: float):
    #     self.s_t = s_t
    #     self._bsm_price = BlackScholes(
    #         S=self.s_t,
    #         K=self.strike,
    #         T=self.maturity,
    #         r=self.risk_free_rate,
    #         Sigma=self.volatility,
    #         OptionType=self.product,
    #     )

    def __post_init__(self):
        super().__post_init__()
        # 驗證 product 的值是否為 call 或 put
        if self.product not in ["call", "put"]:
            raise Exception('Error: product must be "call" or "put".')
        # 驗證 actual_premium 是否有設定
        if self.actual_premium > 0:
            self.actual_premium = self.actual_premium * self.multiplier * self.position
        else:
            raise Exception("Error: please set an actual_premium.")


@dataclass
class Call(Option):
    product: str = "call"


@dataclass
class Put(Option):
    product: str = "put"
