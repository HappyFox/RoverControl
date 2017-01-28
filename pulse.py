import os
import asyncio

async def pulse_task():
    seq = [u"\u25D0", u"\u25D3", u"\u25D1", u"\u25D2"]

    try:
        while True:
            for char in seq:
                print(char + " ", end="", flush=True)
                await asyncio.sleep(0.5)
                print("\r", end="", flush=True)
    except asyncio.CancelledError:
        pass
