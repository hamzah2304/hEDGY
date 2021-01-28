from optibook.synchronous_client import Exchange

import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")

instrument_id = 'PHILIPS_A'

e = Exchange()
a = e.connect()

print("Exchange connected")

#print(e.is_connected())
#result = e.insert_order(instrument_id, price=1., volume=1, side='bid', order_type='limit')
#print(f"Order Id: {result}")
#print(e.is_connected())

orders = e.get_outstanding_orders(instrument_id)
for o in orders.values():
    print(o)
print(orders)

print("Orders checked")