import asyncio
import os
from data import config
from pyrogram import Client
from utils.core import logger, load_from_json, save_list_to_file, save_to_json


class Accounts:
    def __init__(self):
        self.workdir = config.WORKDIR
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH

    @staticmethod
    def get_available_accounts(sessions: list):
        accounts_from_json = load_from_json('sessions/accounts.json')

        if not accounts_from_json:
            raise ValueError("Have not account's in sessions/accounts.json")

        available_accounts = []
        for session in sessions:
            for saved_account in accounts_from_json:
                if saved_account['session_name'] == session:
                    available_accounts.append(saved_account)
                    break

        return available_accounts

    def pars_sessions(self):
        sessions = []
        for file in os.listdir(self.workdir):
            if file.endswith(".session"):
                sessions.append(file.replace(".session", ""))

        logger.info(f"Searched sessions: {len(sessions)}.")
        return sessions

    async def check_valid_account(self, account: dict):
        session_name, phone_number, proxy = account.values()

        try:
            proxy_dict = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            } if proxy else None

            client = Client(name=session_name, api_id=self.api_id, api_hash=self.api_hash, workdir=self.workdir,
                            proxy=proxy_dict)

            connect = await asyncio.wait_for(client.connect(), timeout=config.TIMEOUT)
            if connect:
                await client.get_me()
                await client.disconnect()
                return account
            else:
                await client.disconnect()
        except:
            pass

    async def check_valid_accounts(self, accounts: list):
        logger.info(f"Проверка аккаунтов...")

        tasks = []
        for account in accounts:
            tasks.append(asyncio.create_task(self.check_valid_account(account)))

        v_accounts = await asyncio.gather(*tasks)

        valid_accounts = [account for account, is_valid in zip(accounts, v_accounts) if is_valid]
        invalid_accounts = [account for account, is_valid in zip(accounts, v_accounts) if not is_valid]
        logger.success(f"Доступ получен: {len(valid_accounts)}; Нет доступа: {len(invalid_accounts)}")

        return valid_accounts, invalid_accounts

    async def get_accounts(self):
        sessions = self.pars_sessions()
        available_accounts = self.get_available_accounts(sessions)

        if not available_accounts:
            raise ValueError("Нет доступных аккаунтов")
        else:
            logger.success(f"Поиск доступных аккаунтов: {len(available_accounts)}.")

        valid_accounts, invalid_accounts = await self.check_valid_accounts(available_accounts)

        if invalid_accounts:
            save_list_to_file(f"{config.WORKDIR}invalid_accounts.txt", invalid_accounts)
            logger.info(f"Saved {len(invalid_accounts)} invalid account(s) in {config.WORKDIR}invalid_accounts.txt")

        if not valid_accounts:
            raise ValueError("Нет доступных сессий")
        else:
            return valid_accounts

    async def create_sessions(self):
        while True:
            session_name = input('\nВведите имя сессии:\n Выход - Enter ')
            if not session_name: return

            proxy = input("Введите прокси в формате login:password@ip:port (Enter чтобы продолжить без прокси): ")
            if proxy:
                client_proxy = {
                    "scheme": config.PROXY['TYPE']['TG'],
                    "hostname": proxy.split(":")[1].split("@")[1],
                    "port": int(proxy.split(":")[2]),
                    "username": proxy.split(":")[0],
                    "password": proxy.split(":")[1].split("@")[0]
                }
            else:
                client_proxy, proxy = None, None

            phone_number = (input("Введите номер телефона: ")).replace(' ', '')
            phone_number = '+' + phone_number if not phone_number.startswith('+') else phone_number

            client = Client(
                api_id=self.api_id,
                api_hash=self.api_hash,
                name=session_name,
                workdir=self.workdir,
                phone_number=phone_number,
                proxy=client_proxy,
                lang_code='ru'
            )

            async with client:
                me = await client.get_me()

            save_to_json(f'{config.WORKDIR}accounts.json', dict_={
                "session_name": session_name,
                "phone_number": phone_number,
                "proxy": proxy
            })
            logger.success(f'Добавлен аккаунт {me.username} ({me.first_name}) | {me.phone_number}')

