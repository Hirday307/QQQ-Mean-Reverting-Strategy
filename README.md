# NASDAQ-Correlated Z-Score Mean Reversion Strategy with Momentum-Aware Reallocation
 
## Overview <br>
This algorithm executes a systematic mean reversion strategy by exploiting pricing anomalies between individual NASDAQ-listed stocks and the NASDAQ-100 ETF (QQQ). It dynamically tracks the 10 most correlated stocks to QQQ and trades based on z-score deviations from a historical relationship. Capital is intelligently reallocated using trend momentum filters to maintain market exposure in high-performing assets.
 
## Hypothesis<br>
Stocks that exhibit a strong historical correlation with the NASDAQ index are likely to revert after diverging from typical price relationships. By detecting and trading on these statistical outliers, we aim to capture profits from short-term inefficiencies.
 
## Key Features
•	Dynamic Correlation Tracking: Top 10 QQQ-correlated stocks are selected monthly based on a 252-day rolling Pearson correlation.<br>
•	Z-Score-Based Trading Signals: Entry/exit points are determined by z-score deviations between a stock’s current price and QQQ, normalized by historical MAE and standard deviation.<br>
•	Momentum Filtering: On capital reallocation( Buy/ Sell Signal), funds flow preferentially into/from stocks with bearish/bullish short-term trends.<br>
•	Full Capital Utilization: The portfolio is always fully invested with active rebalancing to avoid idle capital.<br>
•	Immediate Execution: Signals are executed without delay, using daily resolution data.<br>
 
## Signal Logic<br>
Z-Score Calculation<br>
•	For each top stock:<br>
Z = (|Current Error| - Mean Absolute Error) / Standard Deviation of Error<br>
where Error => Stock Price - QQQ Price <br>
### Buy Signal<br>
•	Z-Score ≤ -2<br>
•	The stock is significantly undervalued relative to QQQ.<br>
•	Allocate 10% capital to the stock.<br>
•	Capital is withdrawn proportionally from current bullish holdings.<br>
### Sell Signal<br>
•	Z-Score ≥ 2<br>
•	The stock is significantly overvalued relative to QQQ.<br>
•	Liquidate the position.<br>
•	Reallocate capital to bearish holdings only (based on SMA trend filter).<br>
 
## Portfolio Construction<br>
1.	Stock Universe: Starts with 100 NASDAQ-listed stocks.<br>
2.	Top 10 Selection: Monthly correlation with QQQ over 252-day rolling window.<br>
3.	Monthly Rebalancing: Replace any stocks no longer in top 10 and reset 10% allocation per stock.<br>
4.	On Signal Trades: Positions adjusted based on signals and trend filters.<br>
5.	Momentum Filter: Prioritize reallocating into stocks where SMA(30) > SMA(180).<br>
 
## Execution Details<br>
•	Resolution: Daily<br>
•	Warm-Up: 257 days (to fully populate 252-day RollingWindows)<br>
•	Rolling Windows: Used for historical price tracking of both QQQ and candidate stocks.<br>
•	Capital Efficiency: self.settings.minimum_order_margin_portfolio_percentage = 0 ensures all trades execute regardless of size.<br>
 
## Risk Management<br>
•	No Leverage or Margin<br>
•	Always Fully Invested<br>
•	Selective Reallocation: Bearish assets are avoided when redistributing capital after a sell.<br>
 
## Enhancements Over Traditional Mean Reversion<br>
•	Z-Score over Simple MAE/Std Deviation: Adds probabilistic insight to deviation size.<br>
•	Pairwise Stock-Index Deviation: Tracks error between stock and QQQ directly, instead of against own moving averages.<br>
•	Momentum-Aware Reallocation: Ensures capital flows into upward-trending assets instead of static rebalancing.<br>


**All rights reserved © 2025 Hirdayjeet Singh Bhandal.**
