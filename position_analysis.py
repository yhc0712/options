import numpy as np
import pandas as pd
from options import Option
from dataclasses import dataclass
import matplotlib.pyplot as plt

TXO_MARGIN_A = 44_000
TXO_MARGIN_B = 22_000
TX_INITIAL_MARGIN = 167_000


def Margin_futures(Original_Spot, S_sim, Multiplier, Initial_margin, Position):
    pnl = (S_sim - Original_Spot) * Multiplier * Position

    return -pnl + Initial_margin


def Margin_options(
    Prod, Original_Spot, S_sim, K, T, r, Sigma, Multiplier, Position, A, B
):
    op = Option(
        Prod=Prod,
        Original_Spot=Original_Spot,
        K=K,
        T=T,
        r=r,
        Sigma=Sigma,
        Position=Position,
    )

    if op.Position > 0:
        return 0
    else:
        op.Spot_sim = S_sim
        if op.Prod == "Call":
            Margin = (
                op.bsm_price
                + max(A - max((op.K - op.Original_Spot) * op._Multiplier, 0), B)
            ) * abs(op.Position)
        else:
            Margin = (
                op.bsm_price
                + max(A - max((op.Original_Spot - op.K) * op._Multiplier, 0), B)
            ) * abs(op.Position)

        _op = op
        _op.Spot_sim = _op.Original_Spot

        Pnl = (op.bsm_price - _op.bsm_price) * op._cash_coefficient

        return Margin - Pnl


@dataclass
class Position_analysis:
    _Position: pd.DataFrame = pd.DataFrame(
        columns=[
            "Prod",
            "S",
            "K",
            "T",
            "r",
            "Sigma",
            "Position",
            "Multiplier",
            "Margin",
            "bsm_price",
        ]
    )

    @property
    def Position(self):
        return self._Position

    @Position.setter
    def Position(self, new_position):
        self._Position = new_position

    def new_futures(self, S, Multiplier, Position):
        now = pd.Timestamp.now()
        new_position = pd.DataFrame(
            {"Prod": "Futures", "S": S, "Multiplier": Multiplier, "Position": Position},
            index=[now],
        )
        self.Position = pd.concat([self.Position, new_position], ignore_index=True)

    def new_options(self, Option):
        now = pd.Timestamp.now()
        new_position = pd.DataFrame(
            {
                "Prod": Option.Prod,
                "S": Option.Original_Spot,
                "K": Option.K,
                "T": Option.T,
                "r": Option.r,
                "Sigma": Option.Sigma,
                "Multiplier": Option._Multiplier,
                "Position": Option.Position,
            },
            index=[now],
        )
        self.Position = pd.concat([self.Position, new_position], ignore_index=True)

    def Calculate(self, S_sim):
        self.Position["S_sim"] = np.repeat(S_sim, len(self.Position))

        for i in range(len(self.Position)):
            if self.Position.loc[i, "Prod"] == "Futures":
                self.Position.loc[i, "Cash Delta"] = (
                    self.Position.loc[i, "S_sim"]
                    * self.Position.loc[i, "Multiplier"]
                    * self.Position.loc[i, "Position"]
                )
                self.Position.loc[i, "Cash Gamma"] = 0
                self.Position.loc[i, "Theta"] = 0
                self.Position.loc[i, "Vega"] = 0
                self.Position.loc[i, "Pnl"] = (
                    (self.Position.loc[i, "S_sim"] - self.Position.loc[i, "S"])
                    * self.Position.loc[i, "Multiplier"]
                    * self.Position.loc[i, "Position"]
                )
                self.Position.loc[i, "Margin"] = Margin_futures(
                    self.Position.loc[i, "S"],
                    self.Position.loc[i, "S_sim"],
                    self.Position.loc[i, "Multiplier"],
                    TX_INITIAL_MARGIN,
                    self.Position.loc[i, "Position"],
                )

            elif self.Position.loc[i, "Prod"] in ("Call", "Put"):
                op = Option(
                    Prod=self.Position.loc[i, "Prod"],
                    Original_Spot=self.Position.loc[i, "S"],
                    K=self.Position.loc[i, "K"],
                    T=self.Position.loc[i, "T"],
                    r=self.Position.loc[i, "r"],
                    Sigma=self.Position.loc[i, "Sigma"],
                    Position=self.Position.loc[i, "Position"],
                )
                op.Spot_sim = S_sim
                self.Position.loc[i, "bsm_price"] = op.bsm_price
                self.Position.loc[i, "Cash Delta"] = op.cash_delta
                self.Position.loc[i, "Cash Gamma"] = op.cash_gamma
                self.Position.loc[i, "Theta"] = op.theta
                self.Position.loc[i, "Vega"] = op.vega
                self.Position.loc[i, "Pnl"] = op.pnl
                self.Position.loc[i, "Margin"] = Margin_options(
                    op.Prod,
                    op.Original_Spot,
                    op.Spot_sim,
                    op.K,
                    op.T,
                    op.r,
                    op.Sigma,
                    op._Multiplier,
                    op.Position,
                    TXO_MARGIN_A,
                    TXO_MARGIN_B,
                )

    def Simulation(self, return_upper: float = 0.1, return_lower: float = -0.1):
        df_Simulation = pd.DataFrame(
            columns=[
                "S_sim",
                "Cash Delta",
                "Cash Gamma",
                "Theta",
                "Vega",
                "Pnl",
                "Margin",
            ]
        )

        for i in np.arange(1 + return_lower, 1 + return_upper, 0.01):
            Simulation_spot = round(self.Position.loc[0, "S"] * i, 2)
            self.Calculate(Simulation_spot)
            _df_trade = self.Position.loc[
                :,
                [
                    "Cash Delta",
                    "Cash Gamma",
                    "Theta",
                    "Vega",
                    "Pnl",
                    "Margin",
                ],
            ].sum()
            _df_trade["S_sim"] = Simulation_spot
            _df_trade = _df_trade.to_frame().T
            df_Simulation = pd.concat([df_Simulation, _df_trade], ignore_index=True)
        df_Simulation.set_index(["S_sim"], inplace=True)
        return df_Simulation


market_data = {"S": 10000, "r": 0.01, "Sigma": 0.3, "T": 5 / 252}

pos = Position_analysis()

call_1 = Option(
    Prod="Call",
    Original_Spot=market_data["S"],
    K=10100,
    T=market_data["T"],
    r=market_data["r"],
    Sigma=market_data["Sigma"],
    Position=1,
)
call_2 = Option(
    Prod="Call",
    Original_Spot=market_data["S"],
    K=10150,
    T=market_data["T"],
    r=market_data["r"],
    Sigma=market_data["Sigma"],
    Position=-1,
)
call_3 = Option(
    Prod="Call",
    Original_Spot=market_data["S"],
    K=10100,
    T=market_data["T"],
    r=market_data["r"],
    Sigma=market_data["Sigma"],
    Position=1,
)
put_2 = Option(
    Prod="Put",
    Original_Spot=market_data["S"],
    K=10100,
    T=market_data["T"],
    r=market_data["r"],
    Sigma=market_data["Sigma"],
    Position=1,
)

pos.new_options(call_1)
pos.new_options(call_2)
# pos.new_options(call_3)
# pos.new_options(call_4)


sim = pos.Simulation()

fig, ax1 = plt.subplots(1, 1, sharex=True)
ax1.fill_between(
    sim.index.astype(float),
    sim["Pnl"].astype(float),
    where=sim["Pnl"] >= 0,
    facecolor="green",
    interpolate=True,
    alpha=0.5,
)
ax1.fill_between(
    sim.index.astype(float),
    sim["Pnl"].astype(float),
    where=sim["Pnl"] < 0,
    facecolor="red",
    interpolate=True,
    alpha=0.5,
)

# add a vertical line at y = 0 and label the x value where y = 0
ax1.axhline(y=0, color="black", linestyle="--")
ax1.set_xlabel("Spot")
ax1.set_ylabel("Profit or Loss")
ax1.set_title("Profit Simulation")
ax1.grid(True)
