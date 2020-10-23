from nonebot import on_notice,NoticeSession

@on_notice('group_increase')
async def GroupIncrease(session : NoticeSession):
    await session.send('欢迎[CQ:at,qq={:d}]'.format(session.ctx['user_id']))

@on_notice('group_decrease')
async def GroupDecrease(session:NoticeSession):
    await session.send('{:d}离开了我们'.format(session.ctx['user_id']))