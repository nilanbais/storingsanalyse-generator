import asyncio
import random


async def print_num_range(num_range):
    llist = []
    for i in range(num_range):
        print(i)
        llist.append(i)
        await asyncio.sleep(0.1)

    return sorted(llist, reverse=True)


async def shout_at_random(times_to_shout):
    shouted_numbers = []
    times_shouted = 0

    keep_going = True
    while keep_going:
        num = random.random() * 1000
        print('SHOUTING NUMER %d' % num)
        shouted_numbers.append(num)
        times_shouted += 1

        if times_shouted == times_to_shout:
            keep_going = False

        await asyncio.sleep(random.random())

    return times_shouted, shouted_numbers


async def main(event_loop):
    global y
    task1 = event_loop.create_task(print_num_range(30))
    task2 = event_loop.create_task(shout_at_random(5))
    result = await asyncio.wait([task1, task2])
    # result = await asyncio.gather(task1, task2)
    # result = await asyncio.gather(task1)
    print(f'result in async main() = {result}')
    y = result
    task3 = event_loop.create_task(print_num_range(4))
    task4 = event_loop.create_task(shout_at_random(1))
    result2 = await asyncio.gather(task3, task4)
    print(f'result2 in async main() = {result2}')

if __name__ == '__main__':
    y = 0
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop))
        x = main(loop)
    except Exception as e:
        print(e)
    finally:
        loop.close()
        print(x)
        print(f'result y = {y}')
