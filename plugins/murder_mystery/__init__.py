from nonebot import on_command, CommandSession
from nonebot import permission as perm
from copy import copy
from os import path
from .FSM import FSM, LoadFSM, StoreFSM
from .vote import vote

__plugin_name__ = '剧本杀'
__plugin_usage__ = '剧本杀游戏'


@on_command('剧本杀')
async def murder_mystery(session: CommandSession):
    if session.is_first_run:
        title = session.current_arg_text.strip()
        if title == 'LOAD':
            fsm = LoadFSM('plugins/murder_mystery/tmp/scriptdata')
        else:
            fsm = FSM(session.current_arg_text, session.ctx['group_id'])
    else:
        sender = copy(session.ctx['sender'])
        sender['isSU'] = await perm.check_permission(session.bot, session.ctx, perm.SUPERUSER)
        fsm = session.state['FSM']
        fsm.ReceiveInput(sender, session.current_arg_text)

    session.state['FSM'] = fsm
    if path.exists('plugins/murder_mystery/tmp'):
        StoreFSM(fsm, 'plugins/murder_mystery/tmp/scriptdata')

    ispause = await SessionReply(fsm, session)
    await SendPrivate(fsm, session)
    if ispause:
        session.pause()


async def SessionReply(FSM: FSM, session: CommandSession) -> bool:
    if not FSM.reply:
        return True
    else:
        for r in FSM.reply:
            await session.send(r.msg, at_sender=r.at_sender)
        return FSM.reply[-1].pause


async def SendPrivate(FSM: FSM, session: CommandSession):
    if FSM.private:
        bot = session.bot
        for p in FSM.private:
            await bot.send_private_msg(user_id=p.user_id, message=p.msg)
