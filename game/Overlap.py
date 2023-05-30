from game.Handlers import *
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
        hba.x1 + adjust > hbb.x0:
        right = True
        side = True

    if phba.x0 - adjust >= hbb.x1 and \
        hba.x0 - adjust < hbb.x1:
        left = True
        side = True

    return left, right, side

def vert(hbsa, hbb, adjust = 0):
    hba, phba = hbsa
    up = False
    down = False
    vert = False

    if phba.y1 + adjust <= hbb.y0 and \
        hba.y1 + adjust > hbb.y0:
        down = True
        vert = True

    if phba.y0 - adjust >= hbb.y1 and \
        hba.y0 - adjust < hbb.y1:
        up = True
        vert = True

    return up, down, vert

def spriteToBG(mover, bghits):

    for hit in bghits:
        if overlap(mover.hb, hit):
            left, right, sideh = side( (mover.hb, mover.phb), hit)
            if left:
                rollbackXRight(mover, hit)
            if right:
                rollbackXLeft(mover, hit)

            up, down, verth = vert( (mover.hb, mover.phb), hit)
            if up:
                rollbackYDown(mover, hit)
            if down:
                rollbackYUp(mover, hit)


