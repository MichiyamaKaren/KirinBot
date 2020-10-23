import json
from typing import List, Dict, Union


class Semester:
    class Score:
        def __init__(self, id, courseNameCh, score, gp, **kwargs):
            self.id = str(id)
            self.courseNameCh = courseNameCh
            self.score = score
            self.gp = gp

        def __eq__(self, other):
            iseq = True
            for attr in dir(self):
                if not attr.startswith('_') and not callable(self.__getattribute__(attr)):
                    iseq = iseq and (self.__getattribute__(attr) == other.__getattribute__(attr))
            return iseq

        scorejsondict = Dict[str, str]

        def dictForJSON(self):
            return {'id': self.id, 'courseNameCh': self.courseNameCh, 'score': self.score, 'gp': self.gp}

    def __init__(self, id: str, scores: List[Dict[str, str]], **kwargs):
        self.id: str = str(id)
        self.scores: Dict[str, Semester.Score] = {str(s['id']): self.Score(**s) for s in scores}

    semjsondict = Dict[str, Union[str, List[Score.scorejsondict]]]

    def dictForJSON(self) -> semjsondict:
        return {'id': self.id, 'scores': [s.dictForJSON() for s in self.scores.values()]}


def storeGrade(allsems: Dict[str, Semester], filename='GradeMention/grade.json'):
    jsondict: Dict[str, Semester.semjsondict] = {semid: allsems[semid].dictForJSON() for semid in allsems}
    with open(filename, 'w') as jsonfile:
        json.dump(jsondict, jsonfile)


def loadGrade(filename='GradeMention/grade.json') -> Dict[str, Semester]:
    with open(filename) as jsonfile:
        jsondict: Dict[str, Semester.semjsondict] = json.load(jsonfile)

    allsems = {semid: Semester(**semjson) for semid, semjson in jsondict.items()}
    return allsems


def diffSem(old: Dict[str, Semester], new: Dict[str, Semester]) -> List[Semester.Score]:
    change = []
    for semid in new:
        if semid in old:
            sdictnew = new[semid].scores
            sdictold = old[semid].scores
            for score in sdictnew:
                if score not in sdictold or (not sdictnew[score] == sdictold[score]):
                    change.append(sdictnew[score])
        else:
            for score in new[semid].scores:
                change.append(new[semid].scores[score])
    return change
