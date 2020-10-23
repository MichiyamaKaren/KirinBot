from random import randint
from typing import Optional


class Block:
    def __init__(self):
        self.visible = False
        self.mined = False
        self.flagged = False
        self.minenum = 0

    def show(self, debug=False):
        if self.flagged:
            return 'F'
        elif debug or self.visible:
            if self.mined:
                return 'M'
            else:
                return str(self.minenum)
        else:
            return '  '


class MSMap:
    def __init__(self, size=10, minenum=10):
        self.mapsize = size
        self.minenum = minenum
        self.map = [[Block() for i in range(size)] for j in range(size)]
        self.mine_flagged = 0
        self.flag_without_mine = 0
        self.initMap()

    def initMap(self):
        self.generateMines()
        self.countMines()

    def generateMines(self):
        minecount = 0
        while minecount < self.minenum:
            x = randint(0, self.mapsize - 1)
            y = randint(0, self.mapsize - 1)
            if self.map[x][y].mined:
                continue
            else:
                self.map[x][y].mined = True
                minecount += 1

    def countMines(self):
        maptmp = [[0] * (self.mapsize + 2)] + \
                 [[0] + [int(gij.mined) for gij in self.map[i]] + [0] for i in range(self.mapsize)] \
                 + [[0] * (self.mapsize + 2)]
        for i in range(self.mapsize):
            for j in range(self.mapsize):
                count = 0
                for x in [i, i + 1, i + 2]:
                    for y in [j, j + 1, j + 2]:
                        count += maptmp[x][y]
                count -= maptmp[i + 1][j + 1]
                self.map[i][j].minenum = count

    def tap(self, x, y) -> Optional[bool]:
        if x < 0 or y < 0 or x >= self.mapsize or y >= self.mapsize:
            return
        if self.map[x][y].mined:
            return False
        if self.map[x][y].visible:
            return True

        self.map[x][y].visible = True
        if self.map[x][y].minenum == 0:
            for i in [x - 1, x, x + 1]:
                for j in [y - 1, y, y + 1]:
                    self.tap(i, j)
        return True

    def flag(self, x, y):
        if self.map[x][y].flagged:
            return '({:d},{:d}) already flagged'.format(x, y)
        elif self.map[x][y].visible:
            return 'cannot flag on this block'
        else:
            self.map[x][y].flagged = True
            if self.map[x][y].mined:
                self.mine_flagged += 1
            else:
                self.flag_without_mine += 1
            return '({:d},{:d}) flagged'.format(x, y)

    def unflag(self, x, y):
        if not self.map[x][y].flagged:
            return 'cannot unflag blocks without flag'
        else:
            self.map[x][y].flagged = False
            if self.map[x][y].mined:
                self.mine_flagged -= 1
            else:
                self.flag_without_mine -= 1
            return 'unflagged ({:d},{:d})'.format(x, y)

    def check(self):
        return self.mine_flagged == self.minenum and self.flag_without_mine == 0

    def show(self, debug=False):
        return '\n'.join(
            ['|'.join(['  '] + [str(i) for i in range(self.mapsize)])] +
            [str(i) + '|' + '|'.join(
                [self.map[i][j].show(debug) for j in range(self.mapsize)])
             for i in range(self.mapsize)])


if __name__ == '__main__':
    m = MSMap()
    print(m.show(debug=True))
