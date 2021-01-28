
from optibook.synchronous_client import Exchange


# 1. Work out ideal price - use best bid and best ask price
# Edge cases: no best bid or best ask price

# 2. Hedging section. 
# Find net positions
# If positions > 0: lower sell price or lower buy price (choose) - LOWER SELL - LESS RISKY
# If positions < 0: raise sell price or raise buy price (choose) - RAISE BUY - LESS RISKY
# Weighting tells us how much to raise/lower (choose weighting) 

# 3. Crossover effect
# Work out the spread
# We don't want our sell price lower than or equal to our buy price
# Check whether our orders are bad
# Now assume they are bad
# If positions > 0: we want to sell more - lower buy price
# If positions < 0: we want to sell less - raise the sell price
# 10p above the other price

from optibook.synchronous_client import Exchange

import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')
position = -10

# input: best bid & ask dict ({"bid": bid, "ask": ask})
# output: adjusted bid & ask dict ({"bid": bid, "ask": ask})
def _checkCrossover(bidAskDict):
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

print(_checkCrossover(bidAskDict={"bid": 68.0, "ask": 67.0}))