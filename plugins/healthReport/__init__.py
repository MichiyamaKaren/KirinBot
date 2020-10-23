import nonebot
from nonebot import on_command, CommandSession
from .report import healthReport

__plugin_name__ = 'healthReport'
__plugin_usage__ = '停止：pauseHealthReport/pauseHR\n继续：resumeHealthReport/resumeHR'


@on_command('pauseHealthReport', aliases=('pauseHR',))
async def pause(session: CommandSession):
    nonebot.scheduler.pause_job('healthReport')
    await session.send('已停止')


@on_command('resumeHealthReport', aliases=('resumeHR',))
async def resume(session: CommandSession):
    nonebot.scheduler.resume_job('healthReport')
    await session.send('已恢复')
