import nonebot
import pickle
from datetime import datetime

from typing import Dict, Optional
from nonebot.typing import Context_T
from nonebot.sched import Scheduler

NOTICE_FILE_PATH = 'plugins/notice/notices.pkl'


class Notice:
    def __init__(self, time: datetime, job_id: Optional[str] = None):
        self.time: datetime = time
        self.job_id = job_id

    def set_action_from_nonebot_ctx(self, message: str, ctx: Context_T):
        if ctx['message_type'] == 'private':
            action = 'send_private_msg'
            params = dict(user_id=ctx['user_id'], message=message, self_id=ctx['self_id'])
        elif ctx['message_type'] == 'group':
            action = 'send_group_msg'
            params = dict(group_id=ctx['group_id'], message=message, self_id=ctx['self_id'])
        self.set_action(action=action, params=params)

    def set_action(self, action: str, params: Dict):
        self.action = action
        self.params = params

    @property
    def valid(self) -> bool:
        return self.time > datetime.now()

    def _data_dict(self):
        save_attrs = ['time', 'action', 'params']
        return {attr: self.__getattribute__(attr) for attr in save_attrs}

    def store(self, filename: str, remove_self=False):
        notices = load_notices(filename)
        if remove_self:
            if self.job_id in notices:
                notices.pop(self.job_id)
        else:
            notices[self.job_id] = self
        valid_notices_data = {job_id: notice._data_dict() for job_id, notice in notices.items() if notice.valid}
        with open(filename, 'wb') as f:
            pickle.dump(valid_notices_data, f)

    def register(self, scheduler: Scheduler):
        bot = nonebot.get_bot()

        async def job_func():
            await bot.call_action(self.action, **self.params)

        job = scheduler.add_job(job_func, id=self.job_id, trigger='date', run_date=self.time)
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
            notices_data: Dict[str, Dict] = pickle.load(f)
    except (FileNotFoundError, EOFError):
        return {}

    notices = {}
    for job_id, data in notices_data.items():
        notice = Notice(time=data['time'], job_id=job_id)
        if notice.valid:
            notice.set_action(action=data['action'], params=data['params'])
            notices[notice.job_id] = notice
    return notices


def register_all_valid_notices(filename, scheduler):
    try:
        notices = load_notices(filename)
        for notice in notices.values():
            notice.register(scheduler)
    except FileNotFoundError:
        pass
