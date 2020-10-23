from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from re import match, compile

pattern = compile(r'\s*(\S\s+)+\S\s*$')


@on_command('SpeakSpace')
async def SpeakSpace(session: CommandSession):
    await session.send('你 打 字 带 空 格')


@on_natural_language(only_to_me=False)
async def _(session: NLPSession):
    if match(pattern, session.msg_text):
        return IntentCommand(100, 'SpeakSpace')
