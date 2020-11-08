from nonebot import on_command, CommandSession, scheduler
from datetime import datetime

from .notice import Notice, register_all_valid_notices, NOTICE_FILE_PATH

__plugin_name__ = '自动提醒'
__plugin_usage__ = r'''自动提醒
notice/提醒 时间（格式为：年-月-日 时:分）\n提醒内容，两者用回车分隔'''

register_all_valid_notices(NOTICE_FILE_PATH, scheduler)


@on_command('notice', aliases=('提醒',))
async def noticing(session: CommandSession):
    notice = Notice(time=session.state['time'])
    notice.set_action_from_nonebot_ctx(message=session.state['msg'], ctx=session.ctx)
    notice.register(scheduler)
    await session.send('已设置' + str(session.state['time']) + '的提醒')
    notice.store(NOTICE_FILE_PATH)


@noticing.args_parser
async def _(session: CommandSession):
    arglist = session.current_arg_text.replace('\r', '\n').split('\n')
    if len(arglist) < 2:
        session.finish('格式错误！')
    else:
        try:
            session.state['time'] = datetime.strptime(arglist[0].strip(), '%Y-%m-%d %H:%M')
        except:
            session.finish('时间格式错误！')

        if datetime.now() > session.state['time']:
            session.finish(
                '——如燃烧的宝石般的闪耀，如闪亮的彩虹般幸福的时光，再一次……\n'
                '——行8\n'
                '（服务器运行在平直时空的类时世界线上，无法向过去发送提醒）'
            )

        session.state['msg'] = '[CQ:at,qq={:d}]'.format(session.ctx['user_id']) + '\n'.join(arglist[1:])
