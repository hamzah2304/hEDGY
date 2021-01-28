
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
