import ccxt

# Create an instance of the MXC exchange
api_key = 'mx0vglibXYrmSe1rtX'
api_secret = '7a4c9a5b323c417cbef8f31a6b8f0779'

exchange = ccxt.mexc({
    'apiKey': api_key,
    'secret': api_secret,
})


fix_amount = 6
symbol = 'SOLPEPE/USDT'
ticker = exchange.fetch_ticker(symbol)

# Calculate the amount of base currency to buy
amount = fix_amount / ticker['last']
print('fix amount:', fix_amount)
print('last:', ticker['last'])
print('amount:', amount)

#buy_order = exchange.create_order(symbol, 'market', 'buy', amount, ticker['last'])

balance = exchange.fetch_balance()
print(balance['free'])
amount = balance['free']['SOLPEPE']
print(amount*ticker['last'])
sell_order = exchange.create_order(symbol, 'market', 'sell', amount, ticker['last'])


print(sell_order)
