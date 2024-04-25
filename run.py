import asyncio
import ccxt
import json
import numpy as np
import pandas as pd
import time
from datetime import datetime
from pybot import get_historic
import sys
  

def main_loop(exchange, symbols, curr_dic):
    ##centrase solo en eso y capatar cualquier disparo 20% en el precio
    index = 0
    n=0
    info_list = []
    buy_order = None

    while True:
        hora_corriente = datetime.utcnow()
        if hora_corriente.hour == 13 and hora_corriente.minute == 55:
            start = f'starting loop at: {hora_corriente}'
            print(start)
            info_list.append(start)
            break
        break
        time.sleep(60)

    while(True):
        hora_corriente = datetime.utcnow()
        if hora_corriente.hour == 14 and hora_corriente.minute == 5:
            finish = f'terminando loop a las: {hora_corriente}'
            print(finish)
            info_list.append(finish)
            break

        start_time = time.time()
        ticker_info = []
        perc_dic = {}
        index += 1

        start_fetch_time = time.time()

        """ Fetch ticker last price for all currencys """
        ticker_info = fetch_tickers_with_retry(exchange, symbols)

        fetch_time = time.time() - start_fetch_time

        #print(ticker_info)

        for key in ticker_info.keys():
            price = ticker_info[key]["info"]["lastPrice"]
            """ create currencys dic with curr name and empty list (for prices consulted) """
            try:
                curr_dic[key].append(price)
            except KeyError:
                pass
            ##print('Ultimo precio consultado: ', ticker_info[key]["symbol"], f'  ${price}')
        
        print("┌" + "─" * (22) + "┐")
        if index > 2:
            n += 1

            """
                Algoritmo para calcular la variaciones en el precio
            """
            for key in curr_dic.keys():
                prices = curr_dic[key]

                min_price = float(min(prices))
                max_price = float(max(prices))
                
                """ create info dict for each sign, will only be used for first loop, then it will be edited not created """
                fisrt_price = float(prices[0])
                last_price = float(prices[-1])

                perc = (last_price - fisrt_price) / fisrt_price * 100

                perc_dic[key] = perc
                if perc > 5:
                    """ ejecutar orden de copra a mercado (key es el simbolo)"""
                    symbol = key
                    print(symbol)
                    fix_amount = 7
                    price = last_price
                    amount = fix_amount / last_price
                    if not buy_order:
                        buy_order = retry_order(exchange, symbol, 'buy', amount, price)
                        perc_at_buy = perc
                        print(f'buy {symbol} at {price}, percent {perc_at_buy}%')
                        try:
                            order = exchange.fetch_order(symbol)
                            info_list.append('buy order status: ' + order)
                        except Exception as e:
                            info_list.append(f'fetch_order failed {e}')


                    info = f'precio de {key} salto un {perc}%, a la hora {datetime.utcnow()}'
                    for string in info_list:
                        if info[:31] not in string:
                            info_list.append(info)
                    #print(info)
                try:
                    if 2*perc_at_buy < perc:
                        try:
                            balance = exchange.fetch_balance()
                            amount_bal = balance['free']['MX']
                            sell_order = retry_order(exchange, symbol, 'sell', amount_bal, last_price)
                        except Exception as e:
                            print(f'sell order fail {e}')
                        
                        try:
                            order = exchange.fetch_order(symbol)
                            info_list.append('sell order status: ' + order)
                        except Exception as e:
                            info_list.append(f'fetch_order failed {e}')
                except UnboundLocalError:
                    pass
            
            max_var =  max(perc_dic.values())
            max_key = [key for key, value in perc_dic.items() if value == max_var][0]
            print(f'{len(curr_dic)} monedas monitoreadas, ninguna variacion en el precio significativa: {max_key}: {max_var}')


        loop_time = time.time() - start_time
        print('Loop time:', loop_time, 'seconds')
        print(f'---> {len(ticker_info.keys())} ticker(s) processed in {fetch_time} seconds')
        print("└" + "─" * (22) + "┘")
        print()


    file_path = 'signal.txt'
    with open(file_path, 'w') as file:
        # Write each item in the list to a new line in the file
        for item in info_list:
            file.write(f"{item}\n")

def retry_order(exchange, symbol, side, amount, price):
    try:
        order = exchange.create_order(symbol, 'market', side, amount, price)
        print(f"Sell order placed successfully for {amount} {symbol}")
        return order
    except Exception as e:
        print(f"Error placing {side} of {symbol} order: {e}")
        print("Retrying in 1 second...")
        time.sleep(1)
        retry_order(exchange, symbol, side, amount, price)

def fetch_tickers_with_retry(exchange, symbols, retries=3, delay=1):
    try:
        ticker_info = exchange.fetch_tickers(symbols)
        return ticker_info
    except Exception as e:
        print(f"Failed to fetch tickers: {e}")
        if retries > 0:
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            return fetch_tickers_with_retry(exchange, symbols, retries - 1, delay * 2)
        else:
            raise

async def main():
    # Print the title
    title = 'MEXC bot 1.0'
    print("┌" + "─" * (22) + "┐")
    print("│ " + title.center(20) + " │")
    print("│ " + "    Elegr opcion    " + " │")
    print("│ " + "   1-usar archivo   " + " │")
    print("│ " + "    2-crear nuevo   " + " │")
    print("└" + "─" * (22) + "┘")

    print('hora ahora gmt: ', datetime.utcnow())

    # Create an instance of the MXC exchange
    api_key = 'mx0vglibXYrmSe1rtX'
    api_secret = '7a4c9a5b323c417cbef8f31a6b8f0779'

    exchange = ccxt.mexc({
        'apiKey': api_key,
        'secret': api_secret,
    })
    


    """ Fetch symbols in the exchange """
    
    opt = input("Opcion: ")
    if int(opt) == 1:
        with open('ohlcv.json') as file:
            symbols = json.load(file)
    elif int(opt) == 2:
        print('Requesting symbols...')
        symbols = await get_historic.fetch_candles(exchange)
    
    print("Running...")

    curr_dic = {}
    for sy in symbols:
        """ create currencys dic with curr compared to USDT with empty list (for prices consulted) """
        if '/USDT' in sy:
            curr_dic[sy] = []

    main_loop(exchange, symbols, curr_dic)



if __name__ == '__main__':
    asyncio.run(main())
