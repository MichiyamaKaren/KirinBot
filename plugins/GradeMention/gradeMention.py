import json
import nonebot
from .get_grade_from_web import getGrade
from .grade import loadGrade, storeGrade, diffSem


@nonebot.scheduler.scheduled_job('cron', minute='0,10,20,30,40,50')
async def gradeMention():
    bot = nonebot.get_bot()

    oldsems = loadGrade()
    with open('plugin/GradeMention/config.json') as f:
        config = json.load(f)
    newsems = await getGrade(config['username'], config['password'])
    change = diffSem(oldsems, newsems)
    if change:
        msg = '新出{:d}门成绩'.format(len(change))
        if len(change) < 10:
            msg += '\n' + '\n'.join(
                '{} 成绩：{} 绩点：{}'.format(score.courseNameCh, score.score, score.gp) for score in change)
        await bot.send_private_msg(user_id=2209520605, message=msg, self_id=2891947084)
        await storeGrade(newsems)
