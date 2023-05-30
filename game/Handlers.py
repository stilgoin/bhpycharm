def rollbackXLeft(mover, solid_box):
    mover.xloc = solid_box.x0 - 1 - (mover.hb.width)
# mover.right_impede = True

def rollbackXRight(mover, solid_box):
    mover.xloc = (solid_box.x1 - mover.hb.xoffs) + 1
    # mover.left_impede = True

def rollbackYUp(mover, solid_box):
    mover.yloc = solid_box.y0 - 1 - (mover.hb.height)

def rollbackYDown(mover, solid_box):
    mover.yloc = solid_box.y1 - (mover.hb.yoffs) + 1