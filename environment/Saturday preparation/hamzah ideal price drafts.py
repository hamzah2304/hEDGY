from optibook.synchronous_client import Exchange

import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")
e = Exchange()
a = e.connect()

last_bid_price = 0
last_ask_price = 0
instrument_id = "PHILIPS_A"
# GOAL - return the best bid and best ask price, or create one
while True:
    order_book = e.get_last_price_book(instrument_id=instrument_id)
    """
    #print(order_book.timestamp)
    #print(order_book.instrument_id)
    print(order_book.bids)
    print(order_book.asks)
    
    """
    if not order_book.bids:
        best_bid = last_bid_price
    if not order_book.asks:
        best_ask = last_ask_price
        # INDEPDENT
    if order_book.bids and order_book.asks:    
        best_bid = order_book.bids[0].price
        best_ask = order_book.asks[0].price
        
        last_bid_price = best_bid
        last_ask_price = best_ask
        
        print(best_bid)
        print(best_ask)
        print("")
        print("")
        print("")
    
    