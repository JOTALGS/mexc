import asyncio
import datetime
import ccxt

async def get_filter_symbols(exchange):
    """
        fetch all active symbols in MEXC compared to USDT only
    """

    """ Fetch symbols in the exchange """
    current_datetime = datetime.datetime.now()
    
    symbols = get_symbols(exchange.fetch_markets())
    ##print('cantidad de symbolos', len(symbols))

    """ Fetch ticker last price for all currencys """
    ticker_symbs = exchange.fetch_tickers(symbols)
    curr_dic = {}
    usdt_symbols = []
    for sy in ticker_symbs.keys():
        """ create currencys dic with curr compared to USDT with empty list (for prices consulted) """
        if '/USDT' in sy:
            curr_dic[sy] = []
            usdt_symbols.append(sy)

    symbols = usdt_symbols

    """filter symbols with no movements in price"""
    i = 0
    while (i < 10):
        i += 1
        ticker_info = exchange.fetch_tickers(symbols)
        for key in ticker_info.keys():
            price = ticker_info[key]["info"]["lastPrice"]
            try:
                curr_dic[key].append(price)
            except KeyError:
                pass
        """Wait for 15 seconds"""
        await asyncio.sleep(10)

    ##quiet_symbs_test = {}
    quiet_symbols = []
    for key in curr_dic.keys():
        if all(item == curr_dic[key][0] for item in curr_dic[key]):
            ##quiet_symbs_test[key] = curr_dic[key]
            quiet_symbols.append(key)

    ##print('quiet pre-filter', len(quiet_symbs_test))        
    fetch_time = datetime.datetime.now() - current_datetime
    print('fetched symbols and tickers in: ', fetch_time, 'pre-fiter to:', len(quiet_symbols))

    return quiet_symbols, curr_dic

def get_symbols(list_of_dic):
    symbol_list = []
    for dic in list_of_dic:
        symbol = dic["symbol"]
        symbol_list.append(str(symbol))
    return symbol_list