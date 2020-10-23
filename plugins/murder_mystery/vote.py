from nonebot import on_command, CommandSession
from nonebot import permission as perm
import os
import shelve


@on_command('剧本杀投票', permission=perm.PRIVATE)
async def vote(session: CommandSession):
    self_id = 2891947084
    user_id = session.ctx['user_id']
    vote_success = False
    dir = 'plugins/murder_mystery/tmp'
    if not os.path.exists(dir):
        os.mkdir(dir)
    with shelve.open(os.path.join(dir, 'gamedata')) as gamedata:
        group_id = gamedata['group_id']
        players = gamedata['players']
        if user_id not in players:
            await session.send('你没有参与剧本杀，不能投票')
        else:
            name = session.current_arg_text.strip()
            if name not in players.values():
                await session.send('不存在人名：{}'.format(name))
            else:
                vote = gamedata['vote']
                vote[name] += 1
                gamedata['vote'] = vote
                vote_success = True
                await session.send('你已成功投票给{}'.format(name))

    if vote_success:
        await session.bot.send_group_msg(
            group_id=group_id, self_id=self_id,
            message='[CQ:at,qq={:d}]已完成投票'.format(user_id))
