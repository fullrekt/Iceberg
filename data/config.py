API_ID = 29748423
API_HASH = '5f64b4e1b0e6f7ffa5753e100c0dff69'

DELAYS = {
    'ACCOUNT': [5, 10],  
    'BEFORE_CLAIM': [5, 10],   
    'CHANGE_STATUS_TASK': [6, 9],
}

# title blacklist tasks (do not change)
BLACKLIST_TASKS = ['Invite 5 friends', 'Invite 10 friends', 'Invite 15 friends', 'Invite 30 friends', 'Invite 50 friends', 'Invite 100 friends', 'Upgrade to Iceberg Plus. 1 month', 'Upgrade to Iceberg Plus. 3 month', 'Upgrade to Iceberg Plus. 6 month', 'Upgrade to Iceberg Plus. 1 year', 'Explore Iceberg Pass and grab it now!']

PROXY = {
    "USE_PROXY_FROM_FILE": False,  # True - чтобы юзать прокси из отдельного файла, False - если юзаешь прокси из accounts.json
    "PROXY_PATH": "data/proxy.txt",  # Путь к файлу с прокси
    "TYPE": {
        "TG": "socks5",  
        "REQUESTS": "socks5"  
        }
}

WORKDIR = "sessions/"

TIMEOUT = 30


