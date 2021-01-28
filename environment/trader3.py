import math

# class for an object which will handle trading an instrument using our alogorithm
class Trader():
    # an array to store bid history to reduce volatility
    bidPriceHistory = []
    askPriceHistory = []
    # variable to store the previous quote
    last_bid_price = 1
    last_ask_price = 10000
    
    # variable which specifies how many prior bids we use for our estimate
    HISTORY_COUNT = 1
    
    
    def __init__(self, exchange, instrument, instrumentB, orderVolume, weightingFactor, volumeWeighting):
        self.exchange = exchange
        self.instrument = instrument
        self.instrumentB = instrumentB
        self.orderVolume = orderVolume
        self.weightingFactor = weightingFactor
        self.volumeWeighting = volumeWeighting
    
    
    # input: nothing
    # output: {"bid": bid, "ask": ask}
    def _idealPrice(self):
        # Retrieve order book data
        order_book = self.exchange.get_last_price_book(instrument_id=self.instrument)

        # If there are no bids/asks, we set the bid/ask price to the previous bid/ask price
        # If there are bids/asks, we update our bid/ask price to the current best bid/ask price
        if not order_book.bids:
            best_bid = self.last_bid_price
            # add to quote history array
            self.bidPriceHistory.append(self.last_bid_price)
            
        else:
            self.bidPriceHistory.append(order_book.bids[0].price)
            # the best bid is the average of all we store in our history array
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
        
        # make our bids more competitive than others if we can
        if best_bid - best_ask >= 0.3:
            best_bid += 0.1
            best_ask -= 0.1
        # remove the last element from the array which stores the history of quotes
        if len(self.bidPriceHistory) >= self.HISTORY_COUNT and len(self.askPriceHistory) >= self.HISTORY_COUNT:
            self.bidPriceHistory.pop(0)
            self.askPriceHistory.pop(0)
        
        # return our quote estimates (with some failsafes)
        return {"bid": max(10,best_bid), "ask": min(150,best_ask)}


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
    
    # function that makes sure the spread of our quote is enough to make a profit
    def _checkSpread(self, bidAskDict):
        order_book = self.exchange.get_last_price_book(instrument_id=self.instrumentB)
        # must be greater than the current spread in the market we are hedging in
        if order_book.asks:
            while bidAskDict["ask"] <= order_book.asks[0].price:
                bidAskDict["ask"] += 0.1
        if order_book.bids:
            while bidAskDict["bid"] >= order_book.bids[0].price:
                bidAskDict["bid"] -= 0.1
                
        return bidAskDict
        

    
    # Buys stock in hedging exchange 
    def hedge(self):
        
        # Check number of positions we have in quoting and hedging instrument
        positions = self.exchange.get_positions()
        # Compare number of positions in quoting and hedging instrument
        positionTotal = positions[self.instrument] + positions[self.instrumentB]
        # If we are long overall, we need to sell in the hedging exchange
        if positionTotal > 0:
            # sell at the best available bid price
            order_book = self.exchange.get_last_price_book(instrument_id=self.instrumentB)
            if order_book.bids:
                bestPrice = order_book.bids[0].price
                if bestPrice > self.last_bid_price - 5:
                    self.exchange.insert_order(self.instrumentB, price=bestPrice, volume=positionTotal, side="ask", order_type="ioc")
                
        if positionTotal < 0:
            # buy at the best available ask price
            order_book = self.exchange.get_last_price_book(instrument_id=self.instrumentB)
            if order_book.asks:
                bestPrice = order_book.asks[0].price
                if bestPrice < self.last_ask_price + 5:
                    self.exchange.insert_order(self.instrumentB, price=bestPrice, volume=-positionTotal, side="bid", order_type="ioc")
    
    
    # function to work out how much volume we should be ordering based on our position
    def _decideVolume(self):
        positions = self.exchange.get_positions()
        positionTotal = positions[self.instrument] + positions[self.instrumentB]
        volume_weighting = self.volumeWeighting * abs(positionTotal)
        
        return volume_weighting
    
    # input: nothing
    # output: nothing
    def trade(self):
        positions = self.exchange.get_positions()
        # first delete all outstanding orders
        outstanding = self.exchange.get_outstanding_orders(self.instrument)
        for o in outstanding.values():
            self.exchange.delete_order(self.instrument, order_id=o.order_id)
        
        # using alogorithm determine best prices to trade at
        bidAskDict = self._idealPrice()
        bidAskDict = self._hedgeAdjustor(bidAskDict)
        bidAskDict = self._checkCrossover(bidAskDict)
        bidAskDict = self._checkSpread(bidAskDict)
        
        # adjust volume via weighting
        volume_weighting = self._decideVolume()
        volumeBid = math.floor(min(max(1, self.orderVolume - volume_weighting), 500 - positions[self.instrument]))
        volumeAsk = math.floor(min(max(1, self.orderVolume - volume_weighting), 500 + positions[self.instrument]))
        # insert orders at that price
        if volumeBid > 0:
            self.exchange.insert_order(self.instrument, price=bidAskDict["bid"], volume=volumeBid, side="bid", order_type="limit")
        if volumeAsk > 0:
            self.exchange.insert_order(self.instrument, price=bidAskDict["ask"], volume=volumeAsk, side="ask", order_type="limit")
        
        return bidAskDict
        
    # remove all orders to close the trader
    def close(self):
        outstanding = self.exchange.get_outstanding_orders(self.instrument)
        for o in outstanding.values():
            self.exchange.delete_order(self.instrument, order_id=o.order_id)
        trades = self.exchange.get_trade_history(self.instrument) + self.exchange.get_trade_history(self.instrumentB)
        for t in trades:
            print(f"[TRADED {t.instrument_id}] price({t.price}), volume({t.volume}), side({t.side})")
            