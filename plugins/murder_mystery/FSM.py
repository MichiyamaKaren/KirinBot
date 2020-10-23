from .script import Script
from random import shuffle
import shelve
import os
from typing import List, Dict


class Player:
    def __init__(self, ctx, point):
        self.id = ctx['user_id']
        self.point = point

    def SetCharacter(self, name, script):
        self.name = name
        self.script = script

    def CostPoint(self, cost):
        if self.point < cost:
            raise Exception('not enough point')
        else:
            self.point -= cost


class FSM:
    class replymsg:
        def __init__(self, msg='', at_sender=False, pause=True):
            self.msg = msg
            self.at_sender = at_sender
            self.pause = pause

    class privatemsg:
        def __init__(self, user_id, msg):
            self.user_id = user_id
            self.msg = msg

    def __init__(self, title, group_id):
        self.state = 'key'
        self.title = title
        self.group_id = group_id
        self.players: List[Player] = []
        self.clue_round = 0
        self.clue_i = 0

        self.reply: List[FSM.replymsg] = []
        self.private: List[FSM.privatemsg] = []
        if os.path.exists(os.path.join('plugins', 'murder_mystery', 'script_data', title)):
            self.Reply('剧本杀\n剧本：{}'.format(title))
            self.Reply('请作者输入密钥')
        else:
            self.Reply('剧本不存在', pause=False)

    def ClearReply(self):
        for i in range(len(self.reply)):
            del self.reply[0]
        for i in range(len(self.private)):
            del self.private[0]

    def Reply(self, msg, at_sender=False, pause=True):
        if self.reply:
            pause = self.reply[-1].pause
        self.reply.append(self.replymsg(msg, at_sender, pause))

    def SendPrivate(self, user_id, msg):
        self.private.append(self.privatemsg(user_id, msg))

    def StoreGame(self):
        rootdir = os.path.join('plugins', 'murder_mystery', 'tmp')
        if not os.path.exists(rootdir):
            os.mkdir(rootdir)
        with shelve.open(os.path.join(rootdir, 'gamedata')) as gamedata:
            gamedata['group_id'] = self.group_id
            gamedata['players'] = {player.id: player.name for player in self.players}
            gamedata['vote'] = {name: 0 for name in self.script.characters.keys()}

    def LoadVote(self):
        with shelve.open('plugins/murder_mystery/tmp/gamedata') as gamedata:
            vote = gamedata['vote']
        return vote

    def ReceiveInput(self, sender: Dict, text: str):
        self.ClearReply()

        if text == 'exit' and sender['isSU']:
            self.Reply('强制退出', pause=False)

        if self.state == 'key':
            script = Script(self.title, text)
            if script.KeyVerification():
                self.Reply('密钥正确，开始游戏\n请玩家回复\'sign in\'注册')
                script.LoadScript()
                self.script = script
                self.author_id = sender['user_id']
                self.state = 'sign'
            else:
                self.Reply('密钥错误，请重新输入')

        elif self.state == 'sign':
            if text == 'sign in':
                self.Reply('注册成功', at_sender=True)
                self.players.append(Player(sender, self.script.init_point))
            elif text == 'stop signing':
                self.Reply('停止注册')
                if len(self.players) != len(self.script.characters):
                    self.Reply('玩家数和角色数不符，重新注册')
                    self.players = []
                else:
                    # 分配角色
                    shuffle(self.players)
                    for i, name in enumerate(self.script.characters):
                        self.players[i].SetCharacter(name, self.script.characters[name])
                    self.Reply('角色分配：\n' +
                               '\n'.join(
                                   ['[CQ:at,qq={}]--{}'.format(player.id, player.name) for player
                                    in self.players]
                               ))
                    # 给玩家发送剧本
                    for player in self.players:
                        self.SendPrivate(user_id=player.id, msg=player.script)
                    self.Reply('剧本发送完毕，游戏开始')
                    self.state = 'game'
                    self.StoreGame()

        elif self.state == 'game':
            if text == 'clue':
                self.clue_round += 1
                self.clue_i = 0
                self.players: List[Player] = self.players[-1::-1]
                self.Reply('开始第{:d}轮线索收集'.format(self.clue_round))
                self.state = 'clue'
                self.Reply('目前剩余线索：\n' + self.script.ClueLeft())
                self.Reply('请[CQ:at,qq={:d}]选择线索，你有{:d}点线索点'.format(
                    self.players[0].id, self.players[0].point
                ))
            elif text == 'vote':
                if self.script.nclue:
                    self.Reply('还有没被获取的线索，请开启下一轮线索收集')
                else:
                    self.Reply('开始投票，请私聊发送\'剧本杀投票\'+空格+你认为的真凶的全名')
                    self.state = 'vote'

        elif self.state == 'clue':
            player = self.players[self.clue_i]
            if sender['user_id'] == player.id:
                if text == 'stop':
                    self.Reply('[CQ:at,qq={:d}]的线索获取阶段结束'.format(player.id))
                    # 选择下一名玩家
                    i = self.clue_i + 1
                    while i < len(self.players) and self.players[i].point <= 0:
                        i += 1
                    if i < len(self.players):
                        self.clue_i = i
                        self.Reply('请[CQ:at,qq={:d}]选择线索，你有{:d}点线索点'.format(
                            self.players[i].id, self.players[i].point
                        ))
                    else:
                        self.Reply('本轮线索收集结束，回到游戏进程')
                        self.state = 'game'
                else:
                    try:
                        name, i = text.split()
                        i = int(i)
                        content, hasdeep, cost = self.script.GetClue(name, i)
                        player.CostPoint(cost)
                        self.SendPrivate(player.id, content)
                        self.Reply('选择成功，你还剩{:d}点线索点，回复\'stop\'停止获取'.format(player.point))
                        if hasdeep:
                            self.Reply('这条线索还有深入线索，再次获取这条线索即可得到')
                    except Exception as e:
                        self.Reply('发生错误：{}'.format(e))

        elif self.state == 'vote':
            if text == 'check':
                vote = self.LoadVote()
                self.Reply('投票结束\n' +
                           '\n'.join(['[CQ:at,qq={:d}]得票数{:d}'.format(name, n)
                                      for name, n in vote.items() if n]))
                max_name = max(vote.items(), key=lambda item: item[1])[0]
                if max_name == self.script.true_murderer:
                    self.Reply('恭喜，投票结果正确，你们找到了真凶')
                else:
                    self.Reply('很遗憾，投票结果错误\n真凶是{}'.format(self.script.true_murderer))
                self.Reply('游戏结束', pause=False)


def StoreFSM(fsm, path):
    with shelve.open(path) as scriptFSM:
        scriptFSM['FSM'] = fsm


def LoadFSM(path):
    with shelve.open(path) as scriptFSM:
        fsm = scriptFSM['FSM']
    return fsm
