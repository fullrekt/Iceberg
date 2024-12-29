from utils.core.telegram import Accounts
from utils.starter import start, stats
import asyncio
from data import config
from itertools import zip_longest
from utils.core import get_all_lines
import os


async def main():
    print("Автор софта fullrekt\n")
    action = int(input("Выбери действие:\n1. Запуск\n2. Статистика\n3. Cоздать сессию\n\n> "))

    if action == 3:
        await Accounts().create_sessions()

    if action == 2:
        await stats()

    if action == 1:
        accounts = await Accounts().get_accounts()

        tasks = []

        if config.PROXY['USE_PROXY_FROM_FILE']:
            proxys = get_all_lines(config.PROXY['PROXY_PATH'])
            for thread, (account, proxy) in enumerate(zip_longest(accounts, proxys)):
                if not account: break
                session_name, phone_number, proxy = account.values()
                tasks.append(asyncio.create_task(start(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)))
        else:
            for thread, account in enumerate(accounts):
                session_name, phone_number, proxy = account.values()
                tasks.append(asyncio.create_task(start(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)))

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
