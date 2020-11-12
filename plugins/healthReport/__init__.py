import nonebot
from nonebot import on_command, CommandSession
from .report import healthReport, healthReportWeekly

__plugin_name__ = 'healthReport'
__plugin_usage__ = '''停止：pauseHR\n继续：resumeHR
停止每周报备：pauseHRW\n继续每周报备：resumeHRW'''


@on_command('pauseHealthReport', aliases=('pauseHR',))
async def pause(session: CommandSession):
    nonebot.scheduler.pause_job('healthReport')
    await session.send('已停止')


@on_command('resumeHealthReport', aliases=('resumeHR',))
async def resume(session: CommandSession):
    nonebot.scheduler.resume_job('healthReport')
    await session.send('已恢复')


@on_command('pauseHealthReportWeekly', aliases=('pauseHRW',))
async def pauseW(session: CommandSession):
    nonebot.scheduler.pause_job('healthReportWeekly')
    await session.send('已停止')


@on_command('resumeHealthReportWeekly', aliases=('resumeHRW',))
async def resumeW(session: CommandSession):
    nonebot.scheduler.resume_job('healthReportWeekly')
    await session.send('已恢复')
