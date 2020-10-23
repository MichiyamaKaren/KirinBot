import pickle
import os
from typing import List, Tuple

DATA_PATH = 'plugins/NGWordGame/data.pkl'


class Player:
    def __init__(self, sender):
        self.id = sender['user_id']
        if sender['card']:
            self.name = sender['card']
        elif sender['nickname']:
            self.name = sender['nickname']
        else:
            self.name = str(self.id)
        self.NGword = ''
        self.ingame = True


class PlayerList:
    def __init__(self, groupid):
        self.players: List[Player] = []
        self.nplayer = 0
        self.nset = 0  # number of players with NG word already set
        self.canset = False
        self.groupid = groupid

    def searchid(self, pid):
        for i, p in enumerate(self.players):
            if p.id == pid:
                return i
        return -1

    def __getitem__(self, pid):
        index = self.searchid(pid)
        if index == -1:
            return None
        else:
            return self.players[index]

    def append(self, player: Player):
        if not self[player.id]:
            self.players.append(player)
        self.nplayer += 1

    # tell players[i] to set NG word for players[i+1]
    def setPrompt(self) -> List[Tuple[int, str]]:
        prompt = []
        for i, p in enumerate(self.players):
            msgi = '设置{}的NG词，指令：\nsetNG NG词\n可以覆盖设定' \
                .format(self.players[(i + 1) % self.nplayer].name)
            prompt.append((p.id, msgi))
        return prompt

    # returns True if all players are set
    def setNG(self, i, NG) -> bool:
        if not self.players[i].NGword:
            self.nset += 1
        self.players[i].NGword = NG.lower()
        return self.nset == self.nplayer

    def checkText(self, pid, text):
        p = self[pid]
        if p and p.ingame and p.NGword in text.lower():
            return p
        else:
            return None

    def exitGame(self, pid):
        self[pid].ingame = False
        self.nplayer -= 1

    def winner(self):
        for p in self.players:
            if p.ingame:
                return p
        # 只有一个人玩时会出现此状况，debug用
        return Player({'user_id': 0, 'card': 'nobody'})

    def printPlayers(self, seperate: str = '\n') -> str:
        return seperate.join([p.name for p in self.players])

    def printNG(self, mask=-1) -> str:
        return '\n'.join(p.name + '：' + p.NGword for i, p in enumerate(self.players) if i != mask)


def storePlayer(playerlist: PlayerList, filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))
    with open(filename, 'wb') as f:
        pickle.dump(playerlist, f)


def loadPlayer(filename) -> PlayerList:
    with open(filename) as f:
        playerlist = pickle.load(f)
    return playerlist
