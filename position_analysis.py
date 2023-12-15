import numpy as np
import pandas as pd

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
        

    def new_options(self, CallPut, S, K, T, r, Sigma, Position, Multiplier = 50):
        now = pd.Timestamp.now()
        new_position = pd.DataFrame({
            'Prod': CallPut,
            'S': S,
            'K': K,
            'T': T,
            'r': r,
            'Sigma': Sigma,
            'Multiplier': Multiplier,
            'Position': Position
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
            
            elif self.Position.loc[i, 'Prod'] == 'Call':
                pass

            elif self.Position.loc[i, 'Prod'] == 'Put':
                pass

    def get_position(self):
        
        return self.Position
