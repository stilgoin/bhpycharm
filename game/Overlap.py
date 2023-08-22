from game.Handlers import *
from system.defs import Jump, Facing, Vertical
from enum import IntEnum

class Result(IntEnum):
    NULL = 0xFF
    OVERLAP = 0
    CONTACT = 1

class OverlapResult:
    side = 0
    vert = 0
    facing = 0
    standing = 0
    result = Result.NULL
    hba = None
    phba = None
    phbb = None
    hbb = None
    mva = None
    mvb = None

    def __str__(self):
        return str(self.result) + " " + str(self.side) + " " + str(self.vert) \
            + " " + str(self.facing) + " " + str(self.standing)

def contact(recta, rectb):
    if recta.x0 - 1 > rectb.x1 or \
            recta.x1 + 1 < rectb.x0 or \
            recta.y0 - 1 > rectb.y1 or \
            recta.y1 + 1 < rectb.y0:
        return False

    return True

def overlap(recta, rectb):
    if recta.x0 > rectb.x1 or \
        recta.x1 < rectb.x0 or \
        recta.y0 > rectb.y1 or \
        recta.y1 < rectb.y0:
        return False
    return True


def sideContact(recta, rectb):
    if recta.x0 - 1 == rectb.x1 or \
            recta.x1 + 1 == rectb.x0:

        if recta.y0 > rectb.y1 or \
                recta.y1 < rectb.y0:
            return False
        else:
            return True
    return False
    # return True


def vertContact(recta, rectb):
    if recta.y0 - 1 == rectb.y1 or \
            recta.y1 + 1 == rectb.y0:

        if recta.x0 > rectb.x1 or \
                recta.x1 < rectb.x0:
            return False
        else:
            return True
    return False

def side(hbsa, hbb, adjust = 0):
    hba, phba = hbsa
    right = False
    left = False
    side = False

    if phba.x1 + adjust <= hbb.x0 and \
        hba.x1 + adjust >= hbb.x0:
        right = True
        side = True

    if phba.x0 - adjust >= hbb.x1 and \
        hba.x0 - adjust <= hbb.x1:
        left = True
        side = True

    return left, right, side

def vert(hbsa, hbb, adjust = 0):
    hba, phba = hbsa
    up = False
    down = False
    vert = False

    if phba.y1 + adjust <= hbb.y0 - adjust and \
        hba.y1 + adjust >= hbb.y0 - adjust:
        down = True
        vert = True

    if phba.y0 - adjust >= hbb.y1 + adjust and \
        hba.y0 - adjust <= hbb.y1 + adjust:
        up = True
        vert = True

    return up, down, vert

def moverToMover(mva, mvb) -> OverlapResult:
    result = OverlapResult()
    result.hba = mva.hb
    result.hbb = mvb.hb
    result.phba = mva.phb
    result.phbb = mvb.phb

    if overlap(mva.hb, mvb.hb):
        result.result = Result.OVERLAP
        upa, downa, vertha = vert((mva.hb, mva.phb), mvb.hb)
        upb, downb, verthb = vert((mva.hb, mva.phb), mvb.hb, 1)

        if upa or upb:
            result.vert = Vertical.UP
        if downa or downb:
            result.vert = Vertical.DOWN

        la, ra, sidea = side((mva.hb, mva.phb), mvb.hb)
        lb, rb, sideb = side((mva.hb, mva.phb), mvb.hb, 1)

        if la or lb:
            result.side = Facing.LEFT
        if ra or rb:
            result.side = Facing.RIGHT

    elif contact(mva.hb, mvb.hb):
        result.result = Result.CONTACT
        if sideContact(mva.hb, mvb.hb):
            if mva.facing == Facing.RIGHT \
                and mva.xloc < mvb.xloc:
                result.facing = Facing.RIGHT
            if mva.facing == Facing.LEFT \
                and mva.xloc > mvb.xloc:
                result.facing = Facing.LEFT
            #result.facing = mva.facing
        if vertContact(mva.hb, mvb.hb):
            result.standing = mva.vertical

    return result


def spriteToBG(mover, bghits):
    floor_found = False
    for hit in bghits:

        if contact(mover.hb, hit) and vertContact(mover.hb, hit)\
                and mover.jump_state == Jump.FLOOR:
            rollbackYUp(mover, hit)
            floor_found = True

        if overlap(mover.hb, hit):
            if 1 == hit.solid:
                left, right, sideh = side( (mover.hb, mover.phb), hit)
                if left:
                    rollbackXRight(mover, hit)
                if right:
                    rollbackXLeft(mover, hit)

            upa, downa, vertha = vert( (mover.hb, mover.phb), hit)
            upb, downb, verthb = vert( (mover.hb, mover.phb), hit, 1)
            if upa and 1 == hit.solid:
                rollbackYDown(mover, hit)
            if downa or downb:
                rollbackYUp(mover, hit)
                floor_found = True

    return floor_found


