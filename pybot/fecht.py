import asyncio
import aiohttp
import json


async def gather_api(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            return await response.json()


async def main():
    apis = [    
        'https://www.google.com',
        'https://www.facebook.com',
        'https://www.twitter.com'
    ]
    tasks = [asyncio.ensure_future(gather_api(api) for api in apis)]

    #for api in apis:
    #    tasks.append(api)
    
    responses = await asyncio.gather(*tasks)