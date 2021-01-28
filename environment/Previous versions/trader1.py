# class for an object which will handle trading an instrument using our alogorithm
class Trader():
    bidPriceHistory = []
    askPriceHistory = []
    last_bid_price = 1
    last_ask_price = 10000
    
    HISTORY_COUNT = 4
    
    def __init__(self, exchange, instrument, orderVolume, weightingFactor):
        self.exchange = exchange
        self.instrument = instrument
        self.orderVolume = orderVolume
        self.weightingFactor = weightingFactor
    
    
    # input: nothing
    # output: {"bid": bid, "ask": ask}
    def _idealPrice(self):
        # Retrieve order book data
        order_book = self.exchange.get_last_price_book(instrument_id=self.instrument)

        # If there are no bids/asks, we set the bid/ask price to the previous bid/ask price
        # If there are bids/asks, we update our bid/ask price to the current best bid/ask price
        if not order_book.bids:
            best_bid = self.last_bid_price
            self.bidPriceHistory.append(self.last_bid_price)
            
        else:
            self.bidPriceHistory.append(order_book.bids[0].price)
            best_bid = round(sum(self.bidPriceHistory) / len(self.bidPriceHistory), 1)
            
                
        if not order_book.asks:
            best_ask = self.last_ask_price
            self.askPriceHistory.append(self.last_ask_price)
        else:
            self.askPriceHistory.append(order_book.asks[0].price)
            best_ask = round(sum(self.askPriceHistory) / len(self.askPriceHistory), 1)
            
        # Update previous bid/ask prices
        self.last_bid_price = best_bid
        self.last_ask_price = best_ask
        
        if best_bid - best_ask >= 0.3:
            best_bid += 0.1
            best_ask -= 0.1
        if len(self.bidPriceHistory) > self.HISTORY_COUNT and len(self.askPriceHistory) > self.HISTORY_COUNT:
            self.bidPriceHistory.pop(0)
            self.askPriceHistory.pop(0)
        return {"bid": best_bid, "ask": best_ask}
    
    
    # input: best bid & ask dict ({"bid": bid, "ask": ask})
    # output: adjusted bid & ask dict ({"bid": bid, "ask": ask})
    def _hedgeAdjustor(self, bidAskDict):
        position = self.exchange.get_positions()[self.instrument]
        # if positive position, lower sell price to get rid of stock
        if position > 0:
            bidAskDict["ask"] -= round(position * self.weightingFactor, 1)
        # if negative position, raise buy price to get more stock
        elif position < 0:
            bidAskDict["bid"] -= round(position * self.weightingFactor, 1)
        return bidAskDict
    
    
    # input: best bid & ask dict ({"bid": bid, "ask": ask})
    # output: adjusted bid & ask dict ({"bid": bid, "ask": ask})
    def _checkCrossover(self, bidAskDict):
        position = self.exchange.get_positions()[self.instrument]
        # Here, we check that the ask price is NOT below the bid price, if so, we adjust accordingly
        spread = bidAskDict['ask'] - bidAskDict['bid']
        if spread < 0:
            # Now we change our bid or ask price depending on whether we are long or short overall
            # If long, lower bid price
            if position > 0:
                bidAskDict["bid"] = bidAskDict["ask"] - 0.10
            # If short, raise ask price
            if position <= 0:
                bidAskDict["ask"] = bidAskDict["bid"] + 0.10
        return bidAskDict
    
    
    # input: nothing
    # output: nothing
    def trade(self):
        # first delete all outstanding orders
        outstanding = self.exchange.get_outstanding_orders(self.instrument)
        for o in outstanding.values():
            self.exchange.delete_order(self.instrument, order_id=o.order_id)
        
        # using alogorithm determine best prices to trade at
        bidAskDict = self._idealPrice()
        bidAskDict = self._hedgeAdjustor(bidAskDict)
        bidAskDict = self._checkCrossover(bidAskDict)
        # insert orders at that price
        self.exchange.insert_order(self.instrument, price=bidAskDict["bid"], volume=self.orderVolume, side="bid", order_type="limit")
        self.exchange.insert_order(self.instrument, price=bidAskDict["ask"], volume=self.orderVolume, side="ask", order_type="limit")
        print(f"ORDERS:\n\n\n\n{self.orderVolume} bid orders at {bidAskDict['bid']}\n{self.orderVolume} ask orders at {bidAskDict['ask']}")
        
        
    
    # remove all orders to close the trader
    def close(self):
        outstanding = self.exchange.get_outstanding_orders(self.instrument)
        for o in outstanding.values():
            self.exchange.delete_order(self.instrument, order_id=o.order_id)
        trades = self.exchange.get_trade_history(self.instrument)
        for t in trades:
            print(f"[TRADED {t.instrument_id}] price({t.price}), volume({t.volume}), side({t.side})")
        
        