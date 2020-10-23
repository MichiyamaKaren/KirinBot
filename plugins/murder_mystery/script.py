import hashlib
import os
from typing import Dict, List

script_dir = os.path.join('plugins', 'murder_mystery', 'script_data')


class Clue:
    def __init__(self, content, deep=None, cost=1):
        self.content = content
        self.cost = cost
        self.deep: Clue = deep
        self.n = 1 + self.deep.n if deep else 1

    def Get(self):
        if self.n <= 0:
            raise Exception('clue not available')
        self.n -= 1
        if not self.deep or self.n <= self.deep.n:
            return self.content
        else:
            return self.deep.Get()


class Script:
    def __init__(self, title, key):
        self.title = title
        self.root_dir = os.path.join(script_dir, self.title)
        self.key = key.encode('utf-8')

    def KeyVerification(self):
        keymd5 = hashlib.md5(self.key).hexdigest()
        with open(os.path.join(script_dir, self.title, 'key')) as f:
            keystored = f.read()
        return keymd5 == keystored

    def LoadScript(self):
        # 真凶
        self.true_murderer = self.Decode('true_murderer.txt').strip('\r\n ')
        # 初始情报点
        with open(os.path.join(self.root_dir, 'init_point.txt')) as f:
            self.init_point = int(f.read())
        # 角色剧本
        with open(os.path.join(self.root_dir, 'characters.txt')) as f:
            characters = [chara.strip('\r\n ') for chara in f.read().split('\n')]
        self.characters = {name: self.Decode(name + '.txt') for name in characters}
        # 线索
        clue = self.Decode('clue.txt')
        lines = clue.split('\n')
        self.clue: Dict[str, List[Clue]] = {}
        self.nclue = 0
        cluename = lines[0].strip('\r\n ')
        thisclue = []
        i = 1
        while True:
            if i >= len(lines):
                if thisclue:
                    self.clue[cluename] = thisclue
                    break
            line = lines[i]
            if not line:
                self.clue[cluename] = thisclue
                i += 1
                cluename = lines[i].strip('\r\n ')
                thisclue = []
            else:
                if line.startswith('D'):
                    content = line.strip('D ')
                    i += 1
                    deep = Clue(lines[i])
                    thisclue.append(Clue(content, deep))
                    self.nclue += 2
                else:
                    thisclue.append(Clue(line))
                    self.nclue += 1
            i += 1

    def Decode(self, path):
        # 异或加密的解密算法
        with open(os.path.join(self.root_dir, path + '-encoded'), 'rb') as f:
            msg = f.read()
        ml = len(msg)
        kl = len(self.key)
        key = ml // kl * self.key + self.key[:ml % kl]
        return bytes([mi ^ ki for mi, ki in zip(msg, key)]).decode('gbk')

    def ClueLeft(self):
        available = [(name, ' '.join(['{:d}({:d})'.format(i, clue[i].cost)
                                      for i in range(len(clue)) if clue[i].n]))
                     for name, clue in self.clue.items()]
        return '\n'.join(['{}： {}'.format(name, i) for name, i in available])

    def GetClue(self, name, i):
        if name not in self.clue:
            raise Exception('name doesn\'t exist')
        clue = self.clue[name][i]
        self.nclue -= 1
        return clue.Get(), clue.deep != None, clue.cost
