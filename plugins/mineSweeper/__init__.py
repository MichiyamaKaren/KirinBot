from nonebot import on_command, CommandSession
from .MS import MSMap

__plugin_name__ = '扫雷'
__plugin_usage__ = r'扫雷小游戏，发送minesweep/ms/扫雷开始'


@on_command('minesweep', aliases=('ms', '扫雷'), only_to_me=False)
async def mineSweep(session: CommandSession):
    if session.is_first_run:
        await session.send('扫雷小游戏\n在10x10的格子中找出10个雷\n游戏命令：\n'
                           'tap x y 点击(x,y)格子\n'
                           'flag x y 在(x,y)格子上插旗\n'
                           'unflag x y 拔掉(x,y)上的旗\n'
                           'stop 强制退出')
        msmap = MSMap()
        session.state['msmap'] = msmap
        await session.send(msmap.show())
        session.pause()

    msmap: MSMap = session.get('msmap')
    instr = session.get('instr')
    x, y = session.get('position')
    if instr == 'tap':
        if not msmap.tap(x, y):
            await session.send('you died')
            await session.send(msmap.show(debug=True))
            session.finish()
        else:
            await session.send(msmap.show())
            session.pause('input next instruction')
    elif instr == 'flag':
        await session.send(msmap.flag(x, y))
        if msmap.check():
            await session.send('you win')
            session.finish()
        else:
            await session.send(msmap.show())
            session.pause('input next instruction')
    elif instr == 'unflag':
        await session.send(msmap.unflag(x, y))
        if msmap.check():
            await session.send('you win')
            session.finish()
        else:
            await session.send(msmap.show())
            session.pause('input next instruction')
    elif instr == 'stop':
        await session.send('game finished')
        session.finish()


@mineSweep.args_parser
async def _(session: CommandSession):
    if not session.is_first_run:
        text = session.current_arg_text
        if text[:3] == 'tap':
            session.state['instr'] = 'tap'
            session.state['position'] = [int(i) for i in text.split()[1:3]]
        elif text[:4] == 'flag':
            session.state['instr'] = 'flag'
            session.state['position'] = [int(i) for i in text.split()[1:3]]
        elif text[:6] == 'unflag':
            session.state['instr'] = 'unflag'
            session.state['position'] = [int(i) for i in text.split()[1:3]]
        elif text[:4] == 'stop':
            session.state['instr'] = 'stop'
            session.state['position'] = [-1, -1]
        else:
            session.pause()
