import json
from nonebot import on_command, CommandSession
from .baiduMapAPI import BaiduMap, BaiduAPIException
from .seventimer import weatherAPI

__plugin_name__ = '天气预报'
__plugin_usage__ = '''使用格式：
'天气/weather+地名+城市
可只给出一个参数，此时地名会按照百度地理编码API解析（不一定准）
数据来自晴天钟（http://www.7timer.cn/）'''


@on_command('weather', aliases=('天气',), only_to_me=False)
async def weather(session: CommandSession):
    with open('plugins/weather/config.json') as f:
        ak = json.load(f)['ak']
    baidumap = BaiduMap(ak=ak)
    try:
        if session.state['type'] == 'geocoding':
            lat, lng, p = baidumap.coordinate(session.state['addr'])
        elif session.state['type'] == 'place':
            results = baidumap.place_query(session.state['query'], session.state['region'])
            location = results[0]['location']
            lat, lng = location.lat, location.lon

        addr = baidumap.address(lat=lat, lng=lng)
        await session.send(
            '{}地区预报结果为：\n{}'.format(addr, weatherAPI(lat=lat, lon=lng)))
    except BaiduAPIException as e:
        await session.send('地图API错误：{}'.format(e.msg))


@weather.args_parser
async def _(session: CommandSession):
    args = session.current_arg_text.strip().split()
    if len(args) == 1:
        session.state['type'] = 'geocoding'
        session.state['addr'] = args[0]
    elif len(args) == 2:
        session.state['type'] = 'place'
        session.state['query'], session.state['region'] = args
    else:
        session.finish('参数格式错误！')
