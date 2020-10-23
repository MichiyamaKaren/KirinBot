import pickle
import nonebot
from nonebot import Scheduler, NoneBot
from datetime import datetime
from typing import Dict
from nonebot.typing import Context_T

NOTICE_FILE_PATH = 'plugins/notice/notices.pkl'


def notice_job_func(bot: NoneBot, action: str, params: Dict):
    async def job_func():
        bot.call_action(action, **params)

    return job_func


class Notice:
    def __init__(self, time: datetime, message: str, ctx: Context_T):
        self.time: datetime = time
        self.job_id = None

        message = '[CQ:at,qq={:d}]'.format(ctx['user_id']) + message
        if ctx['message_type'] == 'private':
            self.action = 'send_private_msg'
            self.params = dict(user_id=ctx['user_id'], message=message, self_id=ctx['self_id'])
        elif ctx['message_type'] == 'group':
            self.action = 'send_group_msg'
            self.params = dict(group_id=ctx['group_id'], message=message, self_id=ctx['self_id'])
        elif ctx['message_type'] == 'discuss':
            self.action = 'send_discuss_msg'
            self.params = dict(discuss_id=ctx['discuss_id'], message=message, self_id=ctx['self_id'])

    @property
    def valid(self) -> bool:
        return self.time > datetime.now()

    def store(self, filename: str, remove_self=False):
        notices = load_notices(filename)
        if remove_self:
            notices.pop(self.job_id)
        else:
            notices[self.job_id] = self
        valid_notices = {job_id: notice for job_id, notice in notices.items() if notice.valid}
        with open(filename, 'wb') as f:
            pickle.dump(valid_notices, f)

    def register(self, scheduler: Scheduler):
        notice_func = notice_job_func(nonebot.get_bot(), self.action, self.params)
        job = scheduler.add_job(notice_func, id=self.job_id, trigger='date', run_date=self.time)
        self.job_id = job.id

    def reschedule(self, scheduler: Scheduler, time: datetime):
        scheduler.reschedule_job(self.job_id, trigger='data', run_data=time)
        self.time = time
        self.store(NOTICE_FILE_PATH)

    def remove(self, scheduler: Scheduler):
        scheduler.remove_job(self.job_id)
        self.store(NOTICE_FILE_PATH, remove_self=True)


def load_notices(filename: str) -> Dict[str, Notice]:
    try:
        with open(filename, 'rb') as f:
            notices: Dict[str, Notice] = pickle.load(f)
        return {job_id: notice for job_id, notice in notices.items() if notice.valid}
    except (FileNotFoundError,EOFError):
        return {}


def register_all_valid_notices(filename, scheduler):
    try:
        notices = load_notices(filename)
        for notice in notices.values():
            notice.register(scheduler)
    except FileNotFoundError:
        pass
