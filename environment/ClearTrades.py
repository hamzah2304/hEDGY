from optibook.synchronous_client import Exchange

e = Exchange()
a = e.connect()

# Simple algorithm to clear all current positions so that it is easier to test hedging algorithms

for s, p in e.get_positions().items():
    if p > 0:
        e.insert_order(s, price=1, volume=p, side='ask', order_type='ioc')
    elif p < 0:
        e.insert_order(s, price=100000, volume=-p, side='bid', order_type='ioc')  