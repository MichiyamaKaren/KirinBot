from nonebot import on_command, CommandSession
import requests
import os

__plugin_name__ = 'LaTeX渲染'
__plugin_usage__ = r'发送 LaTeX/latex/tex+表达式，返回渲染结果图片'


@on_command('LaTeX', aliases=('latex', 'tex'), only_to_me=False)
async def OnLaTeX(session: CommandSession):
    latex = session.current_arg_text
    picpath = await getLaTeXpic(latex, session.ctx['user_id'])
    await session.send(r'[CQ:image,file=file:///' + os.path.abspath(picpath) + ']')
    os.remove(picpath)


async def getLaTeXpic(latex, id):
    if not os.path.exists('temp'):
        os.mkdir('temp')
    pic = requests.get(r'http://latex.codecogs.com/png.latex?\bg_white ' + latex)
    filename = 'temp/latex-' + str(id) + '.png'
    with open(filename, 'wb') as f:
        f.write(pic.content)
    return filename
