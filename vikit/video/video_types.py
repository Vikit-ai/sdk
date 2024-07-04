from enum import Enum


class VideoType(Enum):
    COMPROOT = 0
    COMPCHILD = 1
    IMPORTED = 2
    RAWTEXT = 3
    TRANSITION = 4
    PRMPTBASD = 5

    def __str__(self):
        return self.name.lower()
