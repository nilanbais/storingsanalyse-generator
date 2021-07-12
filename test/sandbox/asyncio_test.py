#!/usr/bin/env python3
# asyncio_test.py

import asyncio
import random

# ANSI colors
c = (
    "\033[0m",   # End of color
    "\033[36m",  # Cyan
    "\033[91m",  # Red
    "\033[35m",  # Magenta
)


async def makerandom(idsbs_grouped_df: int, threshold: int = 6) -> int:
    print(c[idsbs_grouped_df + 1] + f"Initiated makerandom({idsbs_grouped_df}).")
    i = random.randint(0, 10)
    while i <= threshold:
        print(c[idsbs_grouped_df + 1] + f"makerandom({idsbs_grouped_df}) == {i} too low; retrying.")
        await asyncio.sleep(idsbs_grouped_df + 1)
        i = random.randint(0, 10)
    print(c[idsbs_grouped_df + 1] + f"---> Finished: makerandom({idsbs_grouped_df}) == {i}" + c[0])
    return i


async def main():
    res = await asyncio.gather(*(makerandom(i, 10 - i - 1) for i in range(3)))
    return res

# if __name__ == "__main__":
#     random.seed(444)
#     r1, r2, r3 = asyncio.run(main())
#     print()
#     print(f"r1: {r1}, r2: {r2}, r3: {r3}")
