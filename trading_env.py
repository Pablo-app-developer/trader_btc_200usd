import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces

class TradingEnv(gym.Env):
    """
    A professional-grade trading environment for Reinforcement Learning.
    Focuses on risk management and realistic market mechanics.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, df, initial_balance=10000, commission=0.0001, window_size=60, 
                 cooldown_steps=8, stop_loss=0.02, trailing_stop_threshold=0.03, 
                 trailing_stop_drop=0.015, risk_aversion=2.5, ema_penalty=0.05, 
                 vol_penalty=0.05, position_size_pct=0.40):
        super(TradingEnv, self).__init__()

        self.df = df.reset_index(drop=True)
        self.window_size = window_size
        self.initial_balance = initial_balance
        self.commission = commission
        
        # Risk Config
        self.cooldown_steps = cooldown_steps
        self.stop_loss = stop_loss
        self.ts_threshold = trailing_stop_threshold
        self.ts_drop = trailing_stop_drop
        self.risk_aversion = risk_aversion
        self.ema_penalty = ema_penalty
        self.vol_penalty = vol_penalty
        self.position_size_pct = position_size_pct

        # Action Space: 0 = Hold, 1 = Buy, 2 = Sell
        self.action_space = spaces.Discrete(3)

        # --- PHASE 3: Features ---
        # 1. Log Returns
        self.df['Log_Ret'] = np.log(self.df['Close'] / self.df['Close'].shift(1)).fillna(0)
        
        # 2. RSI (Normalized 0-1)
        self.df['RSI_Norm'] = self.df['RSI'] / 100.0
        
        # 3. MACD (Momentum Architecture) - REPLACES BOLINGER
        ema_12 = self.df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = self.df['Close'].ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        self.df['MACD_Hist'] = (macd - signal) / self.df['Close'] # Normalized
        self.df['MACD_Hist'] = self.df['MACD_Hist'].fillna(0)
        
        # 4. EMA Distances (Short & Long Term)
        self.df['EMA_20_Dist'] = (self.df['Close'] / self.df['EMA_20']) - 1
        self.df['EMA_50_Dist'] = (self.df['Close'] / self.df['EMA_50']) - 1
        self.df['EMA_200_Dist'] = (self.df['Close'] / self.df['EMA_200']) - 1 # MARKET REGIME

        # Select Features (MOMENTUM FOCUSED)
        self.obs_cols = ['Log_Ret', 'RSI_Norm', 'MACD_Hist', 'EMA_20_Dist', 'EMA_50_Dist', 'EMA_200_Dist']
        self.n_features = len(self.obs_cols) + 2 # +2 for account
        
        # Pre-compute Data Matrix
        self.data_matrix = self.df[self.obs_cols].values.astype(np.float32)
        
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.window_size, self.n_features), dtype=np.float32
        )

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.balance = self.initial_balance
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        self.shares_held = 0
        self.entry_price = 0 # Track Entry Price for Stop Loss
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.total_trades = 0
        
        self.current_step = self.window_size
        self.end_step = len(self.df) - 1
        
        # Inactivity & Cooldown Tracker
        self.steps_since_trade = 0
        self.steps_since_sell = self.cooldown_steps 
        
        # --- PHASE 7: Positional Tracking ---
        self.highest_price_since_entry = 0
        
        return self._next_observation(), {}

    def _next_observation(self):
        # 1. Market Features (Fast Slice)
        market_obs = self.data_matrix[self.current_step - self.window_size : self.current_step]
        
        # 2. Account Features
        balance_ratio = np.log(self.balance / self.initial_balance + 1e-9)
        
        current_price = self.df.iat[self.current_step - 1, self.df.columns.get_loc('Close')]
        position_val = self.shares_held * current_price
        position_ratio = position_val / self.net_worth
        
        account_obs = np.full((self.window_size, 2), [balance_ratio, position_ratio], dtype=np.float32)
        
        # Combine
        obs = np.hstack((market_obs, account_obs))
        
        return np.nan_to_num(obs)

    def step(self, action):
        done = False
        
        # Safe Price
        idx = min(self.current_step, len(self.df) - 1)
        current_price = self.df.iat[idx, self.df.columns.get_loc('Close')]

        # --- PHASE 6.1: Professional Risk Management ---
        reward = 0
        penalty = 0
        
        # 1. Cooldown Logic: Prevent Buy if sold recently
        self.steps_since_sell += 1
        if action == 1 and self.steps_since_sell < self.cooldown_steps:
            action = 0 # Force Hold
            penalty -= 0.05 # Penalty for trying to overtrade
            
        if self.shares_held > 0:
            # Update Highest Price for Trailing Stop
            if current_price > self.highest_price_since_entry:
                self.highest_price_since_entry = current_price
            
            # Calculate Latent PnL
            unrealized_pnl = (current_price - self.entry_price) / self.entry_price
            
            # 2. FIXED STOP LOSS (Mechanical): If it falls 2%, we sell NO MATTER WHAT
            if unrealized_pnl <= -self.stop_loss:
                action = 2 # Force Sell
                penalty -= 0.1 
            
            # 3. TRAILING STOP LOSS (PRO): If we were up >3%, and we drop 1.5% from peak, LOCK PROFITS
            peak_drawdown = (self.highest_price_since_entry - current_price) / self.highest_price_since_entry
            if unrealized_pnl >= self.ts_threshold and peak_drawdown >= self.ts_drop:
                action = 2 # Force Sell to Lock Profit
                reward += 0.05 # Reward for disciplined profit locking
            
            # 4. DYNAMIC TAKE PROFIT: Bonus for big moves
            if unrealized_pnl >= 0.05:
                reward += 0.1 
        
        # 5. EMA 200 TREND FILTER (Institutional Grade)
        ema_200 = self.df.iat[idx, self.df.columns.get_loc('EMA_200')]
        is_bull_market = current_price > ema_200
        
        if action == 1: # Buying
            if is_bull_market:
                reward += 0.02 # Bonus for buying with trend
            else:
                reward -= self.ema_penalty # Penalty for buying against major trend
        elif self.shares_held > 0 and not is_bull_market:
            reward -= 0.01 # Small cost for "holding underwater" in bear market        
        # 4. Volatility Filter: Penalize if BB is too narrow (Low Volatility)
        bb_width = (self.df.iat[idx, self.df.columns.get_loc('BBU_20_2.0')] - self.df.iat[idx, self.df.columns.get_loc('BBL_20_2.0')]) / current_price
        if (action == 1 or action == 2) and bb_width < 0.01: # Less than 1% width
            reward -= self.vol_penalty # Don't trade in a flat market

        # --- Action Execution ---
        trade_executed = False
        invalid_action_penalty = 0

        if action == 1: # Buy
            if self.balance > 10: 
                # Invest configurable % (Default 40%, Challenge 90%+)
                amount_to_invest = self.balance * self.position_size_pct
                if amount_to_invest < 10: amount_to_invest = self.balance
                
                shares_bought = (amount_to_invest / current_price) * (1 - self.commission)
                
                # Update Entry Price
                total_value_before = self.shares_held * self.entry_price
                new_value = shares_bought * current_price
                if self.shares_held + shares_bought > 0:
                    self.entry_price = (total_value_before + new_value) / (self.shares_held + shares_bought)
                
                self.balance -= amount_to_invest
                self.shares_held += shares_bought
                self.highest_price_since_entry = current_price
                trade_executed = True
                self.total_trades += 1
            else:
                invalid_action_penalty = -0.1
                
        elif action == 2: # Sell
            if self.shares_held > 0:
                sale_value = (self.shares_held * current_price) * (1 - self.commission)
                self.balance += sale_value
                self.shares_held = 0
                self.entry_price = 0
                self.highest_price_since_entry = 0
                self.total_shares_sold += 1
                self.steps_since_sell = 0 # Reset cooldown
                trade_executed = True
                
                # Trade Completion Reward (Profit Factor)
                trade_pnl = (sale_value - (self.balance - sale_value) * self.position_size_pct) / ((self.balance - sale_value) * self.position_size_pct) # Rough estimate
                # Let's use a cleaner PnL:
                # We'll stick to net worth change but add 
                reward += 0.05 # Base Reward for closing a trade
            else:
                invalid_action_penalty = -0.1
        
        # 5. Overtrading Friction
        if trade_executed:
            reward -= 0.01 # Every trade has a "tax"
            self.steps_since_trade = 0
        else:
            self.steps_since_trade += 1
            
        # Time Management
        self.current_step += 1
        if self.current_step > self.end_step:
            done = True
        
        # --- Reward Calculation (Nivel Pro) ---
        idx_new = min(self.current_step, len(self.df) - 1)
        next_price = self.df.iat[idx_new, self.df.columns.get_loc('Close')]
        new_net_worth = self.balance + (self.shares_held * next_price)
        
        step_return = (new_net_worth - self.net_worth) / self.net_worth
        
        # 6. INCREASED RISK AVERSION (Professionals hate losing)
        if step_return < 0:
            reward += step_return * self.risk_aversion * 100 # Accumulate, don't overwrite
        else:
            reward += step_return * 100
            
        reward += (penalty + invalid_action_penalty)
        
        # 4. OPPORTUNITY COST PENALTY (Extreme Inactivity)
        if self.shares_held == 0 and self.steps_since_trade > 150:
            reward -= 0.005 

        # Keep the base inactivity penalty too (96 steps)
        if self.shares_held == 0 and self.steps_since_trade > 96:
            reward -= 0.01 
        
        # Drawdown Management
        if new_net_worth > self.max_net_worth:
            self.max_net_worth = new_net_worth
        
        drawdown = (self.max_net_worth - new_net_worth) / self.max_net_worth
        if drawdown > 0.10: 
            reward -= (drawdown * 0.5) 

        # Profit Bonus
        if done and new_net_worth > self.initial_balance:
            reward += 10.0 
        
        self.net_worth = new_net_worth
        
        if self.net_worth <= self.initial_balance * 0.5:
            done = True
            reward = -100 
            
        truncated = False
        
        info = {
            "net_worth": self.net_worth,
            "max_net_worth": self.max_net_worth,
            "shares_held": self.shares_held,
            "trade_executed": trade_executed,
            "total_trades": self.total_trades
        }
        
        return self._next_observation(), reward, done, truncated, info

    def render(self, mode='human', close=False):
        # Rendering logic can be added later for visualization
        print(f'Step: {self.current_step}, Net Worth: {self.net_worth}')
