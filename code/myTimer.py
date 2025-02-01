from settings import *

class Timer:
    def __init__(self, duration, func = None, repeat = None, autostart = False):
        self.duration = duration
        self.start_time = 0
        self.active = False
        self.func = func
        self.repeat = repeat

        if autostart:
            self.activate()

    def __bool__(self):
        return self.active

    def activate(self):
        self.active = True
        self.start_time =pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time =0
        if self.repeat:
            if self.repeat == 'infinite':
                self.activate()
            elif self.repeat > 1:
                self.activate()
                self.repeat -= 1

    def update(self):
        if pygame.time.get_ticks() - self.start_time >= self.duration:
            if self.func and not self.start_time == 0:
                self.func()
            self.deactivate()