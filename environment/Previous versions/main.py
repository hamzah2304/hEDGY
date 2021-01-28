from optibook.synchronous_client import Exchange
from trader2 import Trader
from time import sleep
from threading import Thread
# import matplotlib as plt

e = Exchange()
a = e.connect()

# pnl = []

TIME_PERIOD = 0.2
TIME_RUNNING = 300
TRADES = TIME_RUNNING / TIME_PERIOD
ORDER_VOLUME = 5
WEIGHTING_FACTOR = 0.1/ORDER_VOLUME #0.001
VOLUME_WEIGHTING = 1/2
INSTRUMENT = "PHILIPS_B"

e.poll_new_trades(INSTRUMENT)

diagonosticsOutput = ""

firstTrader = Trader(exchange=e, instrument=INSTRUMENT, instrumentB="PHILIPS_A", orderVolume=ORDER_VOLUME, weightingFactor=WEIGHTING_FACTOR, volumeWeighting = VOLUME_WEIGHTING)
executing = True
count = 0
while executing:
    order_book = e.get_last_price_book(instrument_id="PHILIPS_A")
    # pnl.append(e.get_pnl)
    bidAskDict = firstTrader.trade()
    if count > TRADES:
        executing = False
    count += 1
    sleep(TIME_PERIOD)
    for t in (e.poll_new_trades("PHILIPS_B")):
        
        '''
        diagonosticsOutput += f"[TRADED {t.instrument_id}] price({t.price}), volume({t.volume}), side({t.side})\n"
        diagonosticsOutput += f"Asking in PHILIPS_B for {bidAskDict['ask']}, bidding in PHILIPS_B for {bidAskDict['bid']}\n"
        if order_book.asks and order_book.bids:
            diagonosticsOutput += f"Asking in PHILIPS_A for {order_book.asks[0].price}, bidding in PHILIPS_B for {order_book.bids[0].price}"
        '''
        Thread(target=firstTrader.hedge, args=(t, bidAskDict,)).start()
        

print(diagonosticsOutput)
firstTrader.close()

'''
t = []
count = 0
while count < TIME_RUNNING / TIME_PERIOD:
    t.append(TIME_PERIOD * count)
    count += 1
    
plt.pyplot(t, pnl)
plt.show()
'''