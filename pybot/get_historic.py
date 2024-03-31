import asyncio
import ccxt
from datetime import datetime, timedelta
from . import get_symbols
import json


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
    timeout_list = []
    i=0
    for sy in symbols:
        try:
            symbol_dic[sy] = exchange.fetch_ohlcv(sy, '1h', timestamp)
        except Exception as e:
            timeout_list.append(sy)
            print(f'{sy} timed out - {e}')
            pass
        i += 1
        print(f'{i} out of {len(symbols)}')


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
    print('timeouts', timeout_list)


    file_path = 'ohlcv.json'
    with open(file_path, 'w') as file:
        json.dump(quiet_list, file)

    return quiet_list


def refetch_timeout(list, symbol_dic, exchange, timestamp):
    if len(timeout_list) != 0:
        timeout_list = []
        for sy in list:
            try:
                symbol_dic[sy] = exchange.fetch_ohlcv(sy, '1h', timestamp)
            except Exception as e:
                timeout_list.append(sy)
                print(f'{sy} timed out - {e}')
                pass
            
        refetch_timeout(timeout_list, symbol_dic, exchange, timestamp)

    return symbol_dic

if __name__ == '__main__':
    asyncio.run(fetch_candles())