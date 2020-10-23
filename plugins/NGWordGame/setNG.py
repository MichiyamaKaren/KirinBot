from nonebot import on_command, CommandSession, permission as perm
from .playerlist import PlayerList, storePlayer, loadPlayer, DATA_PATH


@on_command('setNG', permission=perm.PRIVATE)
async def setNG(session: CommandSession):
    playerlist: PlayerList = loadPlayer(DATA_PATH)
    setterid = session.ctx['user_id']
    setteri = playerlist.searchid(setterid)
    text = session.current_arg_text.strip()
    if not playerlist.canset:
        await session.send('现在不能设置NG词')
    elif setteri == -1:
        await session.send('你未注册游戏，不能设置')
    elif not text:
        await session.send('NG词不能为空，请重新设置')
    else:
        seti = (setteri + 1) % playerlist.nplayer
        isallset = playerlist.setNG(seti, text)
        storePlayer(playerlist, DATA_PATH)

        await session.send('你成功设置{}的NG词为“{}”'.format(playerlist.players[seti].name, text))
        await session.bot.send_group_msg(group_id=playerlist.groupid, message=playerlist.players[setteri].name + '完成设置')
        if isallset:
            bot = session.bot
            await bot.send_group_msg(group_id=playerlist.groupid, message='已完成所有NG词设置')
