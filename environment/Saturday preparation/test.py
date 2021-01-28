from optibook.synchronous_client import Exchange


import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")
e = Exchange()
a = e.connect()

instrument = "PHILIPS_A"
# GOAL - return the best bid and best ask price, or create one
def _idealPrice(self, e, instrument):
    e.get_last_price_book(instrument_id=instrument)
    

def checkSpread(bidAskDict):
        order_book = {"bid": 87.5, "ask": 88.5}
        while bidAskDict["ask"] <= order_book["ask"]:
            bidAskDict["ask"] += 0.1
        while bidAskDict["bid"] >= order_book["bid"]:
            bidAskDict["bid"] -= 0.1
        return bidAskDict
        
print(checkSpread({"bid": 88.0, "ask": 88.0}))