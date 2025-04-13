class DisplayEntry:
    id = ""
    animIdx = 0
    frameIdx = 0
    xloc = 0.0
    yloc = 0.0
    fliph = False
    flipv = False
    angle = 0.0

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.animIdx = kwargs['animIdx']
        self.frameIdx = kwargs['frameIdx']
        self.xloc = kwargs['xloc']
        self.yloc = kwargs['yloc']
        self.fliph = kwargs['fliph'] \
            if 'fliph' in kwargs else False
        self.flipv = kwargs['flipv'] \
            if 'flipv' in kwargs else False
        self.angle = kwargs['angle'] \
            if 'angle' in kwargs else 0.0