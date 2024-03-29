import asyncio
import ccxt
from datetime import datetime, timedelta
from . import get_symbols


async def fetch_candles(exchange):
    """
        Fetch all candles and return quiet symbols
    """
    current_datetime = datetime.now()

    symbols, _= await get_symbols.get_filter_symbols(exchange) ##

    fetch_start = datetime.now()
    minutes_ago = current_datetime - timedelta(minutes=80)
    timestamp = int(minutes_ago.timestamp() * 1000)

    symbol_dic = {}
    for sy in symbols:
        symbol_dic[sy] = exchange.fetch_ohlcv(sy, '1h', timestamp)
    
    fetch_time = datetime.now() - fetch_start

    quiet_list = []
    for key in symbol_dic.keys():
        try:
            """ candle high and candle low are equals means no movement """
            if symbol_dic[key][0][2] == symbol_dic[key][0][3]:
                quiet_list.append(key)
        except IndexError:
            pass

    #print(symbol_dic)
    print(f'fetch {len(symbol_dic)} OHLCV\'s in:', fetch_time, 'reduced to: ', len(quiet_list))

    exec_time = datetime.now() - current_datetime
    print('execution time', exec_time)

    return quiet_list

if __name__ == '__main__':
    asyncio.run(fetch_candles())