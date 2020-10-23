from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand


@on_command('mention', aliases=(' '))
async def mentioned(session: CommandSession):
    await session.send('わかります', at_sender=True)


@on_natural_language()
async def _(session: NLPSession):
    # if not matched as any command
    return IntentCommand(60, 'mention')
