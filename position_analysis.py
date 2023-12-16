import numpy as np
import pandas as pd
from options import Option

class Position_analysis():

    def __init__(self):
        self.Position = pd.DataFrame(columns = [
            'Prod',
            'S',
            'K',
            'T',
            'r',
            'Sigma',
            'Position',
            'Multiplier'
        ])

    def new_futures(self, S, Multiplier, Position):
        now = pd.Timestamp.now()
        new_position = pd.DataFrame({
            'Prod': 'Futures',
            'S': S,
            'Multiplier': Multiplier,
            'Position': Position
        }, index=[now])
        self.Position = pd.concat([self.Position, new_position], ignore_index=True)
        

    def new_options(self, Option):
        now = pd.Timestamp.now()
        new_position = pd.DataFrame({
            'Prod': Option.Prod,
            'S': Option.S,
            'K': Option.K,
            'T': Option.T,
            'r': Option.r,
            'Sigma': Option.Sigma,
            'Multiplier': Option.Multiplier,
            'Position': Option.Position
        }, index=[now])
        self.Position = pd.concat([self.Position, new_position], ignore_index=True)
        
    def Calculate(self, S_sim):
        self.Position['S_sim'] = np.repeat(S_sim, len(self.Position))

        for i in range(len(self.Position)):
            
            if self.Position.loc[i, 'Prod'] == 'Futures':

                self.Position.loc[i, 'Cash Delta'] = self.Position.loc[i, 'S_sim'] * self.Position.loc[i, 'Multiplier'] * self.Position.loc[i, 'Position']
                self.Position.loc[i, 'Cash Gamma'] = 0
                self.Position.loc[i, 'Theta'] = 0
                self.Position.loc[i, 'Vega'] = 0
                self.Position.loc[i, 'Pnl'] = (self.Position.loc[i, 'S_sim'] - self.Position.loc[i, 'S']) * self.Position.loc[i, 'Multiplier'] * self.Position.loc[i, 'Position']
            
            elif self.Position.loc[i, 'Prod'] in ('Call', 'Put'):
                op = Option(Prod=self.Position.loc[i, 'Prod'], S=self.Position.loc[i, 'S'], K=self.Position.loc[i, 'K'], T=self.Position.loc[i, 'T'], r=self.Position.loc[i, 'r'], Sigma=self.Position.loc[i, 'Sigma'], Position=self.Position.loc[i, 'Position'])
                op.update_greeks(S_sim=S_sim)
                self.Position.loc[i, 'Cash Delta'] = op.cash_delta
                self.Position.loc[i, 'Cash Gamma'] = op.cash_gamma
                self.Position.loc[i, 'Theta'] = op.theta
                self.Position.loc[i, 'Vega'] = op.vega
                self.Position.loc[i, 'Pnl'] = op.pnl


    def get_position(self):
        
        return self.Position
