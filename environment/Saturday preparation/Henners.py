from optibook.synchronous_client import Exchange

e = Exchange()
a = e.connect()

bidAsk = {"bid": 70.0, "ask": 71.0}
def _hedgeAdjustor(exchange, instrument, bidAskDict, multiplier):
    position = exchange.get_positions()[instrument]
    position = 10
    # if positive position, lower sell price to get rid of stock
    if position > 0:
        bidAskDict["ask"] -= round(position * multiplier, 2)
    # if negative position, raise buy price to get more stock
    elif position < 0:
        bidAskDict["bid"] -= round(position * multiplier, 2)
    return bidAskDict

print(_hedgeAdjustor(exchange=e, instrument="PHILIPS_A", bidAskDict=bidAsk, multiplier=0.05))