from enum import Enum
from .playerlist import Player, PlayerList, storePlayer, loadPlayer, DATA_PATH
from typing import List

states = Enum('gamestate', ['signing', 'settingNG', 'listening'])


class NGFSM:
    class ReplyMsg:
        def __init__(self, msg: str = '', at_sender: bool = False, pause: bool = True):
            self.msg = msg
            self.at_sender = at_sender
            self.pause = pause

    class PrivateMsg:
        def __init__(self, user_id, msg):
            self.user_id = user_id
            self.msg = msg

    def __init__(self, groupid):
        self.state = states.signing
        self.playerlist = PlayerList(groupid)
        self.reply: List[NGFSM.ReplyMsg] = \
            [self.ReplyMsg(msg='NG词语游戏\n请有意参加的成员回复\'sign in\'')]
        self.private: List[NGFSM.PrivateMsg] = []

    def _clearReply(self):
        self.reply = []
        self.private = []

    def recieveInput(self, sender, text):
        self._clearReply()

        if text == 'stop' and sender['isSU']:
            self.reply = [self.ReplyMsg(msg=self.playerlist.printNG()),
                          self.ReplyMsg(msg='游戏强制终止', pause=False)]
            return

        if self.state == states.signing:
            if text == 'sign in':
                self.playerlist.append(Player(sender))
                self.reply = [self.ReplyMsg(msg='成功注册', at_sender=True)]
            elif text == 'stop signing' and sender['isSU']:
                self.reply = [self.ReplyMsg('玩家注册阶段结束，已注册的玩家有：\n' + self.playerlist.printPlayers()),
                              self.ReplyMsg('开始私聊设置NG词')]
                self.private = [self.PrivateMsg(user_id=pid, msg=msg) for pid, msg in self.playerlist.setPrompt()]
                self.playerlist.canset = True
                storePlayer(self.playerlist, DATA_PATH)
                self.state = states.settingNG

        elif self.state == states.settingNG:
            if text == 'check' and sender['isSU']:
                self.playerlist = loadPlayer(DATA_PATH)
                self.playerlist.canset = False
                storePlayer(self.playerlist, DATA_PATH)

                self.reply = [self.ReplyMsg('所有NG词已设置完成，请各位自由谈话')]
                self.private = \
                    [self.PrivateMsg(user_id=p.id,
                                     msg='除你以外所有人的NG词是：\n' +
                                         self.playerlist.printNG(mask=i))
                     for i, p in enumerate(self.playerlist.players)]

                self.state = states.listening

        elif self.state == states.listening:
            p = self.playerlist.checkText(sender['user_id'], text)
            if p:
                self.reply = [self.ReplyMsg('触发了NG词“{}”，退出游戏'.format(p.NGword), at_sender=True)]
                self.playerlist.exitGame(p.id)
                if self.playerlist.nplayer <= 1:
                    winner = self.playerlist.winner()
                    self.reply.append(
                        self.ReplyMsg('游戏结束，{}胜利，ta的NG词是“{}”'.format(winner.name, winner.NGword), pause=False))
                else:
                    self.reply.append(self.ReplyMsg('游戏继续，还有{:d}位玩家'.format(self.playerlist.nplayer)))
