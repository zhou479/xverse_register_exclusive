import requests
import json
import time
from loguru import logger
from faker import Faker
import time
import random
import string

fake = Faker()
def generate_proxystr(length=8):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    proxy_str = f'abc:abc-{random_string}_def@geo.iproyal.com:32325'    # 从iproyal获取代理账户. 也可使用其他代理, 代理格式为 user:password@ip:port
    return proxy_str

def random_delay(min_delay=1, max_delay=5):
    delay_time = random.uniform(min_delay, max_delay)
    time.sleep(delay_time)

def user_exit(segwit_address, taoroot_address, proxies, ua):
    url = f"https://wallet.xverse.app/api/registrations?btcAddress={segwit_address}&ordinalAddress={taoroot_address}"

    payload = {}
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://wallet.xverse.app/whitelist',
    'user-agent': ua
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload, proxies=proxies, stream=True)
        logger.info(response.content)
    except Exception as err:
        logger.debug(f'exit函数执行错误')

def register(segwit_address, taoroot_address):
    proxyUrl = generate_proxystr()
    proxies = {
        'http': 'socks5://' + proxyUrl,
        'https': 'socks5://' + proxyUrl
    }
    ua = fake.chrome()
    # user_exit(segwit_address, taoroot_address, proxies, ua)
    random_delay(1,2)
    url = "https://wallet.xverse.app/api/register"
    
    payload = json.dumps({
        "btcAddress": segwit_address,
        "ordinalAddress": taoroot_address,
        "eventId": "1"
    })
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://wallet.xverse.app',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://wallet.xverse.app/whitelist',
    'user-agent': ua
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)
        if 200 <= response.status_code < 300:
            logger.success(f'注册成功 {response.content}')
        else:
            logger.error(f'注册返回失败 {response.content}')
    except Exception as err:
        logger.error(f'注册请求失败 {err}')

with open('address.json', 'r') as json_file:
    data = json.load(json_file)

segwit_addresses = data["segwit"]
taproot_addresses = data["taproot"]

total_addresses = len(segwit_addresses)
for i, (segwit_address, taproot_address) in enumerate(zip(segwit_addresses, taproot_addresses), start=1):
    logger.debug(f"正在处理第 {i} 个地址/总地址 {total_addresses}")
    logger.info(f'{segwit_address}, {taproot_address}')
    register(segwit_address, taproot_address)
    random_delay()

