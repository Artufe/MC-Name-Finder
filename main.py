import logging
import asyncio
import sys

import aiohttp


async def check(name, session, sem):
    async with sem, session.get(f"https://api.ashcon.app/mojang/v2/user/{name}") as resp:
        resp_json = await resp.json()
        if "code" not in resp_json and "error" not in resp_json:
            return False, name

        return resp_json['code'], name


async def main(total, max_len=10):
    logFormatter = logging.Formatter("[%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO) # logging.DEBUG to see taken names

    fileHandler = logging.FileHandler("log.log")  # log.log.log.log.txt
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    sem = asyncio.Semaphore(40)
    async with aiohttp.ClientSession() as session:
        for x in range(total):
            words = await session.get('https://random-word-api.herokuapp.com/word?number=25')
            words = await words.json()
            tasks = [asyncio.create_task(check(word[:max_len], session, sem)) for word in words]
            results = await asyncio.gather(*tasks)
            for status, name in results:
                if status == 404:
                    rootLogger.info(f"{name}: Not Taken !!!")  # TODO add some alert or idk just pay attention
                elif status == 400:
                    rootLogger.warning(f"{name}: Bad request, not supposed to happen?")
                elif not status:
                    rootLogger.debug(f"{name}: Taken")
                else:
                    rootLogger.debug("Huh?", status, name)



if __name__ == '__main__':
    TOTAL = 20 # 25 names per round for x (20) rounds
    MAX_LEN = 5
    asyncio.run(main(TOTAL, MAX_LEN))
