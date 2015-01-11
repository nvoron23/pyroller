from math import sqrt, cos, sin, pi
import pygame
import sys

PY2 = sys.version_info[0] == 2
string_types = None
text_type = None
if PY2:
    string_types = basestring
    text_type = unicode
else:
    string_types = text_type = str


class Task(pygame.sprite.Sprite):
    """Execute functions at a later time and optionally loop it
    """
    def __init__(self, callback, interval=0, loops=1, args=None, kwargs=None):
        assert (callable(callback))
        assert (loops >= -1)
        super(Task, self).__init__()
        self.interval = interval
        self.loops = loops
        self.callback = callback
        self._timer = 0
        self._args = args if args else list()
        self._kwargs = kwargs if kwargs else dict()
        self._loops = loops

    def update(self, delta):
        self._timer += delta
        if self._timer >= self.interval:
            self._timer -= self.interval
            self.callback(*self._args, **self._kwargs)
            if not self._loops == -1:
                self._loops -= 1
                if self._loops <= 0:
                    self.kill()


class Animation(pygame.sprite.Sprite):
    """Change numeric values over time

    To animate a target sprite/object's position, simply specify
    the target x/y values where you want the widget positioned at
    the end of the animation.  Then call start while passing the
    target as the only parameter.
        ani = Animation(x=100, y=100, duration=1000)
        ani.start(sprite)

    You can also specify a callback that will be executed when the
    animation finishes:
        ani.callback = my_function

    Animations must be added to a sprite group in order for them
    to be updated.  If the sprite group that contains them is
    drawn, then an exception will be raised, so you should create
    a sprite group for only containing Animations.

    When the Animation has finished, then it will remove itself
    from the sprite group that contains it.

    You can optionally delay the start of the animation using the
    delay keyword.

    Note: if you are using pygame rects are a target, you should
    pass 'round_values=True' to the constructor to avoid jitter
    caused by integer truncation.
    """
    def __init__(self, **kwargs):
        super(Animation, self).__init__()
        self._targets = None
        self._started = False
        self._round_values = kwargs.get('round_values', False)
        self._duration = float(kwargs.get('duration', 1000.))
        self._delay = kwargs.get('delay', 0)
        self._transition = kwargs.get('transition', 'linear')
        if isinstance(self._transition, string_types):
            self._transition = getattr(AnimationTransition, self._transition)
        self._elapsed = 0.
        for key in ('duration', 'transition', 'round_values', 'delay'):
            kwargs.pop(key, None)
        self.props = kwargs

    def update(self, dt):
        """Update the animation.
        The unit of time passed must match the one used
        in the constructor.

        :param dt: Time passed since last update.
        """
        self._elapsed += dt
        if self._elapsed < self._delay:
            return

        p = min(1., self._elapsed / self._duration)
        t = self._transition(p)
        for target, props in self._targets:
            for name, values in props.items():
                a, b = values
                value = (a * (1. - t)) + (b * t)
                if self._round_values:
                    value = int(round(value, 0))
                setattr(target, name, value)

        if p >= 1.:
            self._targets = None
            self.kill()
            if hasattr(self, 'callback'):
                self.callback()

    def start(self, sprite):
        """Start the animation on a target sprite/object

        Target must have the attributes that were set when
        this animation was created.

        :param sprite: Any valid python object
        """
        self._targets = [(sprite, dict())]
        for target, props in self._targets:
            for name, value in self.props.items():
                props[name] = getattr(target, name), value


class AnimationTransition(object):
    """Collection of animation functions to be used with the Animation object.
    Easing Functions ported to Kivy from the Clutter Project
    http://www.clutter-project.org/docs/clutter/stable/ClutterAlpha.html

    The `progress` parameter in each animation function is in the range 0-1.
    """

    @staticmethod
    def linear(progress):
        """.. image:: images/anim_linear.png"""
        return progress

    @staticmethod
    def in_quad(progress):
        """.. image:: images/anim_in_quad.png
        """
        return progress * progress

    @staticmethod
    def out_quad(progress):
        """.. image:: images/anim_out_quad.png
        """
        return -1.0 * progress * (progress - 2.0)

    @staticmethod
    def in_out_quad(progress):
        """.. image:: images/anim_in_out_quad.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p
        p -= 1.0
        return -0.5 * (p * (p - 2.0) - 1.0)

    @staticmethod
    def in_cubic(progress):
        """.. image:: images/anim_in_cubic.png
        """
        return progress * progress * progress

    @staticmethod
    def out_cubic(progress):
        """.. image:: images/anim_out_cubic.png
        """
        p = progress - 1.0
        return p * p * p + 1.0

    @staticmethod
    def in_out_cubic(progress):
        """.. image:: images/anim_in_out_cubic.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p * p
        p -= 2
        return 0.5 * (p * p * p + 2.0)

    @staticmethod
    def in_quart(progress):
        """.. image:: images/anim_in_quart.png
        """
        return progress * progress * progress * progress

    @staticmethod
    def out_quart(progress):
        """.. image:: images/anim_out_quart.png
        """
        p = progress - 1.0
        return -1.0 * (p * p * p * p - 1.0)

    @staticmethod
    def in_out_quart(progress):
        """.. image:: images/anim_in_out_quart.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p * p * p
        p -= 2
        return -0.5 * (p * p * p * p - 2.0)

    @staticmethod
    def in_quint(progress):
        """.. image:: images/anim_in_quint.png
        """
        return progress * progress * progress * progress * progress

    @staticmethod
    def out_quint(progress):
        """.. image:: images/anim_out_quint.png
        """
        p = progress - 1.0
        return p * p * p * p * p + 1.0

    @staticmethod
    def in_out_quint(progress):
        """.. image:: images/anim_in_out_quint.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p * p * p * p
        p -= 2.0
        return 0.5 * (p * p * p * p * p + 2.0)

    @staticmethod
    def in_sine(progress):
        """.. image:: images/anim_in_sine.png
        """
        return -1.0 * cos(progress * (pi / 2.0)) + 1.0

    @staticmethod
    def out_sine(progress):
        """.. image:: images/anim_out_sine.png
        """
        return sin(progress * (pi / 2.0))

    @staticmethod
    def in_out_sine(progress):
        """.. image:: images/anim_in_out_sine.png
        """
        return -0.5 * (cos(pi * progress) - 1.0)

    @staticmethod
    def in_expo(progress):
        """.. image:: images/anim_in_expo.png
        """
        if progress == 0:
            return 0.0
        return pow(2, 10 * (progress - 1.0))

    @staticmethod
    def out_expo(progress):
        """.. image:: images/anim_out_expo.png
        """
        if progress == 1.0:
            return 1.0
        return -pow(2, -10 * progress) + 1.0

    @staticmethod
    def in_out_expo(progress):
        """.. image:: images/anim_in_out_expo.png
        """
        if progress == 0:
            return 0.0
        if progress == 1.:
            return 1.0
        p = progress * 2
        if p < 1:
            return 0.5 * pow(2, 10 * (p - 1.0))
        p -= 1.0
        return 0.5 * (-pow(2, -10 * p) + 2.0)

    @staticmethod
    def in_circ(progress):
        """.. image:: images/anim_in_circ.png
        """
        return -1.0 * (sqrt(1.0 - progress * progress) - 1.0)

    @staticmethod
    def out_circ(progress):
        """.. image:: images/anim_out_circ.png
        """
        p = progress - 1.0
        return sqrt(1.0 - p * p)

    @staticmethod
    def in_out_circ(progress):
        """.. image:: images/anim_in_out_circ.png
        """
        p = progress * 2
        if p < 1:
            return -0.5 * (sqrt(1.0 - p * p) - 1.0)
        p -= 2.0
        return 0.5 * (sqrt(1.0 - p * p) + 1.0)

    @staticmethod
    def in_elastic(progress):
        """.. image:: images/anim_in_elastic.png
        """
        p = .3
        s = p / 4.0
        q = progress
        if q == 1:
            return 1.0
        q -= 1.0
        return -(pow(2, 10 * q) * sin((q - s) * (2 * pi) / p))

    @staticmethod
    def out_elastic(progress):
        """.. image:: images/anim_out_elastic.png
        """
        p = .3
        s = p / 4.0
        q = progress
        if q == 1:
            return 1.0
        return pow(2, -10 * q) * sin((q - s) * (2 * pi) / p) + 1.0

    @staticmethod
    def in_out_elastic(progress):
        """.. image:: images/anim_in_out_elastic.png
        """
        p = .3 * 1.5
        s = p / 4.0
        q = progress * 2
        if q == 2:
            return 1.0
        if q < 1:
            q -= 1.0
            return -.5 * (pow(2, 10 * q) * sin((q - s) * (2.0 * pi) / p))
        else:
            q -= 1.0
            return pow(2, -10 * q) * sin((q - s) * (2.0 * pi) / p) * .5 + 1.0

    @staticmethod
    def in_back(progress):
        """.. image:: images/anim_in_back.png
        """
        return progress * progress * ((1.70158 + 1.0) * progress - 1.70158)

    @staticmethod
    def out_back(progress):
        """.. image:: images/anim_out_back.png
        """
        p = progress - 1.0
        return p * p * ((1.70158 + 1) * p + 1.70158) + 1.0

    @staticmethod
    def in_out_back(progress):
        """.. image:: images/anim_in_out_back.png
        """
        p = progress * 2.
        s = 1.70158 * 1.525
        if p < 1:
            return 0.5 * (p * p * ((s + 1.0) * p - s))
        p -= 2.0
        return 0.5 * (p * p * ((s + 1.0) * p + s) + 2.0)

    @staticmethod
    def _out_bounce_internal(t, d):
        p = t / d
        if p < (1.0 / 2.75):
            return 7.5625 * p * p
        elif p < (2.0 / 2.75):
            p -= (1.5 / 2.75)
            return 7.5625 * p * p + .75
        elif p < (2.5 / 2.75):
            p -= (2.25 / 2.75)
            return 7.5625 * p * p + .9375
        else:
            p -= (2.625 / 2.75)
            return 7.5625 * p * p + .984375

    @staticmethod
    def _in_bounce_internal(t, d):
        return 1.0 - AnimationTransition._out_bounce_internal(d - t, d)

    @staticmethod
    def in_bounce(progress):
        """.. image:: images/anim_in_bounce.png
        """
        return AnimationTransition._in_bounce_internal(progress, 1.)

    @staticmethod
    def out_bounce(progress):
        """.. image:: images/anim_out_bounce.png
        """
        return AnimationTransition._out_bounce_internal(progress, 1.)

    @staticmethod
    def in_out_bounce(progress):
        """.. image:: images/anim_in_out_bounce.png
        """
        p = progress * 2.
        if p < 1.:
            return AnimationTransition._in_bounce_internal(p, 1.) * .5
        return AnimationTransition._out_bounce_internal(p - 1., 1.) * .5 + .5
