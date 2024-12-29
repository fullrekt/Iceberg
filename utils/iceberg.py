import random
import time
from datetime import datetime
from utils.core import logger
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.functions.messages import RequestWebView
import asyncio
from urllib.parse import unquote, quote
from data import config
import aiohttp
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import string



def retry_async(max_retries=2):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            thread, account = args[0].thread, args[0].account
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    logger.error(f"Thread {thread} | {account} | Error: {e}. Retrying {retries}/{max_retries}...")
                    await asyncio.sleep(10)
                    if retries >= max_retries:
                        break
        return wrapper
    return decorator


class IcebergBot:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)
        

    async def logout(self):
        await self.session.close()

    async def stats(self):
        await self.login()

#       await self.client.start()
#      response = await self.join_channel('@icebergen')
#      response = await self.join_channel('@icebergcis')
#      print(response)

        r = await (await self.session.get("https://0xiceberg.com/api/v1/web-app/balance/", proxy=self.proxy)).json()

        balance = r.get('amount')
        referral_link = "https://t.me/IcebergAppBot/IcebergPlay?startapp=referral_638199800"

        await asyncio.sleep(random.uniform(5, 7))


        r = await (await self.session.get("https://0xiceberg.com/api/v1/web-app/referral/?page=1&page_size=15", proxy=self.proxy)).json()
        referrals = r.get('count')

        await self.logout()
        await self.client.connect()
        me = await self.client.get_me()

        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

        return [phone_number, name, balance, referrals, referral_link, proxy]

    @staticmethod
    def iso_to_unix_time(iso_time: str):
        return int(datetime.fromisoformat(iso_time.replace("Z", "+00:00")).timestamp()) + 1

    @staticmethod
    def current_time():
        return int(time.time())
    
 #   async def join_channel(self, channel_id: int):
  #      try:
   #         await self.client.join_chat(channel_id)
    #        return "Вы успешно подписались на канал!"
     #   except PeerIdInvalid:
      #      return f"Не удалось подписаться на канал: некорректный ID канала {channel_id}."
       # except Exception as e:
        #    return f"Не удалось подписаться на канал: {str(e)}"

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        query = await self.get_tg_web_data()

        if query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None

        self.session.headers['X-Telegram-Auth'] = query
        return True

    async def get_farming(self):
        resp = await self.session.get('https://0xiceberg.com/api/v1/web-app/farming/', proxy=self.proxy)
        if not await resp.text():
            return None, None

        resp_json = await resp.json()
        start_time = resp_json.get('start_time')
        stop_time = resp_json.get('stop_time')

        return self.iso_to_unix_time(start_time), self.iso_to_unix_time(stop_time)

    async def start_farming(self):
        resp = await self.session.post('https://0xiceberg.com/api/v1/web-app/farming/', proxy=self.proxy)
        resp_json = await resp.json()

        start_time = resp_json.get('start_time')
        stop_time = resp_json.get('stop_time')

        return self.iso_to_unix_time(start_time), self.iso_to_unix_time(stop_time)

    async def claim_points(self):
        resp = await self.session.delete('https://0xiceberg.com/api/v1/web-app/farming/collect/', proxy=self.proxy)
        return resp.status == 201, (await resp.json()).get('amount')
    

    async def change_status(self, task_id: int, status: str):
        await asyncio.sleep(random.uniform(*config.DELAYS['CHANGE_STATUS_TASK']))
        json_data = {"status": status}
        resp = await self.session.patch(f'https://0xiceberg.com/api/v1/web-app/tasks/task/{task_id}/', json=json_data, proxy=self.proxy)

        return (await resp.json()).get('success')

    async def get_tasks(self):
        resp = await self.session.get('https://0xiceberg.com/api/v1/web-app/tasks/', proxy=self.proxy)
        return await resp.json()
    

    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            await self.client.send_message('IcebergAppBot', f'/start refferal_{'id аккаунта куда гнать рефов'}' )
            await asyncio.sleep(2)

            web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('IcebergAppBot'),
                bot=await self.client.resolve_peer('IcebergAppBot'),
                platform='android',
                from_bot_menu=False,
                url='https://0xiceberg.com/webapp/'
            ))


            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = query.split('query_id=')[1].split('&user=')[0]
            user = quote(query.split("&user=")[1].split('&auth_date=')[0])
            auth_date = query.split('&auth_date=')[1].split('&hash=')[0]
            hash_ = query.split('&hash=')[1]

            return f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}"
        except:
            return None
        




