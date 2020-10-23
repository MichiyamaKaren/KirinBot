import requests
import json
from .grade import Semester


async def login(session, username, password):
    loginurl = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin'
    formdata = {'model': 'uplogin.jsp', 'service': 'https://jw.ustc.edu.cn/ucas-sso/login',
                'username': username, 'password': password}
    session.post(loginurl, data=formdata)


async def getJSON(session, url, params=None):
    return json.loads(session.get(url, params=params).text)


async def getGrade(username, password):
    s = requests.session()
    await login(s, username, password)
    grade_sheet = await getJSON(s, 'https://jw.ustc.edu.cn/for-std/grade/sheet/getGradeList?trainTypeId=1&semesterIds')
    return grade_sheet['overview'], {str(sem['id']): Semester(**sem) for sem in grade_sheet['semesters']}
