from optibook.synchronous_client import Exchange
from trader3 import Trader
from time import sleep
from threading import Thread

# Use README for more detail on strategy and functions

e = Exchange()
a = e.connect()

TIME_PERIOD = 0.13
TIME_RUNNING = 1200
TRADES = TIME_RUNNING / TIME_PERIOD
ORDER_VOLUME = 24
WEIGHTING_FACTOR = 0.1/ORDER_VOLUME 
VOLUME_WEIGHTING = 1/2
INSTRUMENT = "PHILIPS_B"

e.poll_new_trades(INSTRUMENT)

diagonosticsOutput = ""

firstTrader = Trader(exchange=e, instrument=INSTRUMENT, instrumentB="PHILIPS_A", orderVolume=ORDER_VOLUME, weightingFactor=WEIGHTING_FACTOR, volumeWeighting = VOLUME_WEIGHTING)
executing = True
count = 0
while executing:
    firstTrader.trade()
    firstTrader.hedge()
    
    # This is a last-minute strategy to take advantage of other people's inefficient algorithms
    # We set up very favourable orders in an attempt to catch those without appropriate checks on their order volume and price
    e.insert_order("PHILIPS_B", price=20.1, volume=300, side="bid", order_type="limit")
    e.insert_order("PHILIPS_B", price=139.9, volume=300, side="ask", order_type="limit")
    
    if count > TRADES:
        executing = False
    count += 1
    sleep(TIME_PERIOD)

print(diagonosticsOutput)
firstTrader.close()
