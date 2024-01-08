import aiohttp
import asyncio

async def main():
    client = aiohttp.ClientSession()

    # response = await client.post(
    #     'http://127.0.0.1:8080/advertisement',
    #     json={'title': 'Movers are required', 'description': 'Salary from 50 thousand', 'owner': 'Denim corp.'},
    # )
    response = await client.delete(
        'http://127.0.0.1:8080/advertisement/1',
    )
    response = await client.get(
        'http://127.0.0.1:8080/advertisement/11',
    )
    print(response.status)
    print(await response.json())
    await client.close()

asyncio.run(main())