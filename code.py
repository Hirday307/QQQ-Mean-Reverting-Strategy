# region imports
from AlgorithmImports import *
# endregion
import numpy as np

class LogicalApricotShark(QCAlgorithm):

    def initialize(self):

        self.set_start_date(2020, 1, 1)
        self.set_end_date(2025, 1, 1)
        self.set_cash(100000)

        self.settings.minimum_order_margin_portfolio_percentage = 0
        
        self.symbols = []
        self.symbol_data={}
        self.cor_window = 252
        self.top_10 = []

        self.nasdaq = self.add_equity("QQQ", Resolution.DAILY).symbol
        self.nasdaq_price = RollingWindow[float](self.cor_window)
        self.tickers = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "NVDA", "TSLA", "NFLX", "ADBE", "AVGO",
            "PEP", "COST", "CSCO", "TMUS", "AMD", "INTC", "QCOM", "AMAT", "TXN", "INTU",
            "ISRG", "ADP", "MDLZ", "VRTX", "REGN", "GILD", "MU", "LRCX", "BKNG", "MAR",
            "ATVI", "PANW", "FTNT", "CRWD", "SPLK", "ZS", "DOCU", "ROST", "KDP", "CTAS",
            "WBD", "EA", "BIDU", "JD", "PDD", "NXPI", "KLAC", "MRVL", "CDNS", "SNPS",
            "ASML", "ANSS", "ADSK", "WDAY", "PAYX", "MNST", "CHTR", "IDXX", "ILMN", "BIIB",
            "EXC", "SIRI", "NTES", "TEAM", "DDOG", "OKTA", "MDB", "ALGN",
            "MCHP", "ENPH", "SEDG", "BMRN", "DXCM", "VRSK", "CPRT", "FAST", "PCAR",
            "CDW", "INCY", "SGEN", "MTCH", "VRSN", "FOXA", "FOX", "TTWO", "DLTR", "EBAY", "CTSH", "XEL", "AEP", "LULU", "UAL", "EXPE", "WBA", "ORLY"]
        
        for i in self.tickers:
            symbl = self.add_equity(i, Resolution.DAILY).symbol
            self.symbols.append(symbl)
            price = RollingWindow[float](self.cor_window)
            
            self.symbol_data[symbl] = {'corr':0.0, 'price':price}

        self.set_warm_up(self.cor_window + 5, Resolution.DAILY)
        self.schedule.on(self.date_rules.month_start("QQQ"), self.time_rules.after_market_open("QQQ", 30), self.rebalance)



    def on_data(self, data: Slice):

        if self.nasdaq in data and data[self.nasdaq] is not None:
            price_nasdaq = data[self.nasdaq].close
            self.nasdaq_price.add(price_nasdaq)
            for i in self.symbols:
                if i in data and data[i] is not None:
                    price = data[i].close
                    self.symbol_data[i]['price'].Add(price)
                self.symbol_data[i]['price'].Add(self.symbol_data[i]['price'][0])

        if self.is_warming_up:
            return

        if self.nasdaq not in data or data[self.nasdaq] is None:
            return

        b = list(self.nasdaq_price)
        if len(b) < 252:
            return
        for i in self.top_10:

            a = list(self.symbol_data[i]['price'])
            if len(a) < 252:
                continue
            if i not in data or data[i] is None:
                continue  # skip if either bar is missing
            
            mean_error = np.mean([abs(a - b) for a, b in zip( a, b)])
            current_error = abs( data[i].close - data[self.nasdaq].close)
            std_error = np.std([abs(a - b) for a, b in zip( a, b)])
            if mean_error !=0:
                z_score = (current_error - mean_error) / std_error

            self.log(f"[OnData] {i.value}: Z Score = {z_score:.2f}, Current Error = {current_error:.2f}, Mean error = {mean_error:.2f}")

            #Sell Signal
            if z_score >= 2 :

                self.log(f"[OnData] SELL Signal: {i.value}, Z Score = {z_score:.2f}")

                weight_tobe_freed = self.portfolio[i].holdings_value / self.portfolio.total_holdings_value
                self.liquidate(i)

                self.prfrd_list = self.top_10
                c = []
                c = [kvp for kvp in self.top_10 if (self.portfolio[kvp].holdings_value > 0) ]
                weight_tobe_raised =  weight_tobe_freed / float(len(c)) 

                bearish_stock = [kv for kv in c if (( (np.mean(list(self.symbol_data[kv]['price'])[:30])) < (np.mean(list(self.symbol_data[kv]['price'])[:180])))) ]
                if len(bearish_stock)>0:
                    weight_tobe_raised =  weight_tobe_freed / float(len(bearish_stock))
                    self.prfrd_list = bearish_stock
                
                for h in self.prfrd_list:

                    if self.portfolio[h].holdings_value > 0:

                        ws = (self.portfolio[h].holdings_value / self.portfolio.total_holdings_value) + weight_tobe_raised
                        self.set_holdings(h, ws)
                        self.log(f"[OnData] Reweighted {h.value} to {ws:.4f}")

            #Buy Signal
            if z_score <= -2:

                self.log(f"[OnData] BUY Signal: {i.value}, Z Score = {z_score:.2f}")

                hlp = []
                self.top_10_hlp = self.top_10
                hlp = [kvp for kvp in self.top_10 if (self.portfolio[kvp].holdings_value > 0) ]
                bullish_stock = [kv for kv in hlp if (((np.mean(list(self.symbol_data[kv]['price'])[:30])) > (np.mean(list(self.symbol_data[kv]['price'])[:180])))) ]
                
                count= len(bullish_stock)
                if len(bullish_stock) > 0:
                    count = sum(1 for kvp in self.top_10 if (self.portfolio[kvp].holdings_value > 0) )
                    self.top_10_hlp = bullish_stock

                for g in self.top_10_hlp:

                    weight_tobe_reduced = 0.1 / count if count != 0 else 0
                    x = (self.portfolio[g].holdings_value / self.portfolio.total_holdings_value) - weight_tobe_reduced
                    weight = x if x > 0 else 0

                    if weight > 0:
                        self.set_holdings(g,weight)
                        self.log(f"[OnData] Reweighted {g.value} to {weight:.4f}")

                self.set_holdings(i, 0.1)
                self.log(f"[OnData] Bought {i.value} at 0.1 weight")

    def rebalance(self):

        if self.is_warming_up:
            return

        corr_list = []
        qqq_prices = list(self.nasdaq_price)
        if len(qqq_prices) < 252:
            return

        self.log("[Rebalance] Starting correlation analysis...")

        for i in self.symbols:

            stock_prices = list(self.symbol_data[i]['price'])
            if len(stock_prices) < 252:
                continue

            corr_matrix = np.corrcoef(qqq_prices, stock_prices)
            corr = corr_matrix[0, 1]
 
            self.symbol_data[i]['corr'] = corr
            corr_list.append((i , corr))
            self.log(f"[Rebalance] {i.value} correlation with QQQ: {corr:.4f}")


        temp = sorted(corr_list, key=lambda x: x[1], reverse=True)[:10]
        new_top_10 = [symbol for symbol, corr in temp]
        self.log(f"[Rebalance] Top 10 Correlated Stocks: {[s.value for s in new_top_10]}")


        for i in self.top_10:
            if i not in new_top_10:
                self.log(f"[Rebalance] Liquidating {i.value} - no longer in top 10")
                self.liquidate(i)

        self.top_10 = new_top_10

        for i in self.top_10:
            self.set_holdings( i, 0.1)
            self.log(f"[Rebalance] Buying {i.value} at 10% weight")
