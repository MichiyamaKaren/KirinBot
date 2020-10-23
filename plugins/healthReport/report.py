import nonebot

import json
import requests
from bs4 import BeautifulSoup

from time import sleep
from random import random


async def login(session, username, password):
    loginurl = r'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
    formdata = {'model': 'uplogin.jsp', 'service': r'https://weixine.ustc.edu.cn/2020/caslogin',
                'username': username, 'password': password}
    r = session.post(loginurl, data=formdata)
    soup = BeautifulSoup(r.content)
    return soup.find('input', attrs={'name': '_token'})['value']


async def report(session, token):
    form_data = dict(
        _token=token,
        now_address=1, gps_now_address='', now_province=340000, gps_province='', now_city=340100, gps_city='',
        now_detail='', is_inschool=4, body_condition=1, body_condition_detail='', now_status=2, now_status_detail='',
        has_fever=0,
        last_touch_sars=0, last_touch_sars_date='', last_touch_sars_detail='',
        last_touch_hubei=0, last_touch_hubei_date='', last_touch_hubei_detail='',
        last_cross_hubei=0, last_cross_hubei_date='', last_cross_hubei_detail='',
        return_dest=1, return_dest_detail='', other_detail=''
    )
    header = {
        'user-agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'accept': r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'content-length': '480',
        'content-type': r'application/x-www-form-urlencoded',
        'origin': r'https://weixine.ustc.edu.cn',
        'referer': r'https://weixine.ustc.edu.cn/2020/home',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1'
    }
    return session.post(r'https://weixine.ustc.edu.cn/2020/daliy_report', data=form_data, headers=header)


@nonebot.scheduler.scheduled_job('cron', id='healthReport', hour=10)
async def healthReport():
    sleep(random() * 600)  # randomly sleep 0-10 minutes

    session = requests.session()
    with open('plugins/healthReport/config.json') as f:
        config = json.load(f)
    token = await login(session, config['username'], config['password'])
    await report(session, token)

    bot = nonebot.get_bot()
    await bot.send_private_msg(user_id=2209520605, message='今日已健康打卡', self_id=2891947084)
