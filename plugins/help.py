from nonebot import on_command, CommandSession, get_loaded_plugins

__plugin_name__ = 'help'
__plugin_usage__ = r'''@机器人发送help/usage获得帮助
发送help+插件名获得插件的帮助'''


@on_command('help', aliases=('usage',), only_to_me=True)
async def help(session: CommandSession):
    plugins = list(filter(lambda p: p.name, get_loaded_plugins()))
    arg = session.current_arg_text.strip().lower()
    if not arg:
        await session.send('KirinBot\nお持ちなさい、あなたが望んだその星を\n\n'
                           '指令列表：\n' + '\n'.join(p.name for p in plugins))
    else:
        for p in plugins:
            if p.name.lower() == arg:
                await session.send(p.usage)
                return
        await session.send('无此指令')
