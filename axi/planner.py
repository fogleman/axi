from __future__ import division

from collections import namedtuple
from itertools import groupby
from math import sqrt, hypot

EPS = 1e-9

_Point = namedtuple('Point', ['x', 'y'])

class Point(_Point):
    def length(self):
        return hypot(self.x, self.y)

    def normalize(self):
        d = self.length()
        if d == 0:
            return Point(0, 0)
        return Point(self.x / d, self.y / d)

    def distance(self, other):
        return hypot(self.x - other.x, self.y - other.y)

    def add(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def sub(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def mul(self, factor):
        return Point(self.x * factor, self.y * factor)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def lerps(self, other, s):
        v = other.sub(self).normalize()
        return self.add(v.mul(s))

Triangle = namedtuple('Triangle',
    ['s1', 's2', 't1', 't2', 'vmax', 'p1', 'p2', 'p3'])

def triangle(s, vi, vf, a, p1, p3):
    # compute a triangular profile: accelerating, decelerating
    s1 = (2 * a * s + vf * vf - vi * vi) / (4 * a)
    s2 = s - s1
    vmax = (vi * vi + 2 * a * s1) ** 0.5
    t1 = (vmax - vi) / a
    t2 = (vf - vmax) / -a
    p2 = p1.lerps(p3, s1)
    return Triangle(s1, s2, t1, t2, vmax, p1, p2, p3)

Trapezoid = namedtuple('Trapezoid',
    ['s1', 's2', 's3', 't1', 't2', 't3', 'p1', 'p2', 'p3', 'p4'])

def trapezoid(s, vi, vmax, vf, a, p1, p4):
    # compute a trapezoidal profile: accelerating, cruising, decelerating
    t1 = (vmax - vi) / a
    s1 = (vmax + vi) / 2 * t1
    t3 = (vf - vmax) / -a
    s3 = (vf + vmax) / 2 * t3
    s2 = s - s1 - s3
    t2 = s2 / vmax
    p2 = p1.lerps(p4, s1)
    p3 = p1.lerps(p4, s - s3)
    return Trapezoid(s1, s2, s3, t1, t2, t3, p1, p2, p3, p4)

def corner_velocity(s1, s2, vmax, a, delta):
    # compute a maximum velocity at the corner of two segments
    # https://onehossshay.wordpress.com/2011/09/24/improving_grbl_cornering_algorithm/
    cosine = -s1.vector.dot(s2.vector)
    if abs(cosine - 1) < EPS:
        return 0
    sine = sqrt((1 - cosine) / 2)
    if abs(sine - 1) < EPS:
        return vmax
    v = sqrt((a * delta * sine) / (1 - sine))
    return min(v, vmax)

class Piece(object):
    # a piece is a constant acceleration for a duration of time
    # the planner generates these pieces
    def __init__(self, p1, p2, v1, acceleration, duration):
        self.p1 = p1
        self.p2 = p2
        self.v1 = v1
        self.v2 = v1 + acceleration * duration
        self.acceleration = acceleration
        self.duration = duration

    def point(self, t):
        return self.p1.lerps(self.p2, self.distance(t))

    def distance(self, t):
        return self.v1 * t + self.acceleration * t * t / 2

    def velocity(self, t):
        return self.v1 + self.acceleration * t

class Segment(object):
    # a segment is a line segment between two points, which will be broken
    # up into pieces by the planner
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.length = p1.distance(p2)
        self.vector = p2.sub(p1).normalize()
        self.max_entry_velocity = 0
        self.entry_velocity = 0
        self.pieces = []

class Planner(object):
    # a planner has a constant acceleration and a max crusing velocity
    def __init__(self, acceleration, max_velocity, corner_factor, jerk):
        self.acceleration = acceleration
        self.max_velocity = max_velocity
        self.corner_factor = corner_factor
        self.jerk = jerk

    def plan(self, points):
        a = self.acceleration
        vmax = self.max_velocity

        # make sure points are Point objects
        points = [Point(x, y) for x, y in points]

        # create segments for each consecutive pair of points
        segments = [Segment(p1, p2) for p1, p2 in zip(points, points[1:])]

        # compute a max_entry_velocity for each segment
        # based on the angle formed by the two segments at the vertex
        for s1, s2 in zip(segments, segments[1:]):
            v = corner_velocity(s1, s2, vmax, a, self.corner_factor)
            s2.max_entry_velocity = v

        # add a dummy segment at the end to force a final velocity of zero
        segments.append(Segment(points[-1], points[-1]))

        # loop over segments
        i = 0
        while i < len(segments) - 1:
            # pull out some variables
            segment = segments[i]
            next_segment = segments[i + 1]
            s = segment.length
            vi = segment.entry_velocity
            vexit = next_segment.max_entry_velocity
            p1 = segment.p1
            p2 = segment.p2

            # determine which profile to use for this segment
            # TODO: rearrange these cases for better flow?

            # accelerate? /
            vf = sqrt(vi * vi + 2 * a * s)
            if vf <= vexit:
                t = (vf - vi) / a
                segment.pieces = [
                    Piece(p1, p2, vi, a, t),
                ]
                next_segment.entry_velocity = vf
                i += 1
                continue

            # accelerate, cruise, decelerate? /---\
            m = triangle(s, vi, vexit, a, p1, p2)
            if m.s1 > -EPS and m.s2 > -EPS and m.vmax >= vmax:
                z = trapezoid(s, vi, vmax, vexit, a, p1, p2)
                segment.pieces = [
                    Piece(z.p1, z.p2, vi, a, z.t1),
                    Piece(z.p2, z.p3, vmax, 0, z.t2),
                    Piece(z.p3, z.p4, vmax, -a, z.t3),
                ]
                next_segment.entry_velocity = vexit
                i += 1
                continue

            # accelerate, decelerate? /\
            if m.s1 > -EPS and m.s2 > -EPS:
                segment.pieces = [
                    Piece(m.p1, m.p2, vi, a, m.t1),
                    Piece(m.p2, m.p3, m.vmax, -a, m.t2),
                ]
                next_segment.entry_velocity = vexit
                i += 1
                continue

            # too fast! update max_entry_velocity and backtrack
            segment.max_entry_velocity = sqrt(vexit * vexit + 2 * a * s)
            i -= 1 # TODO: support non-zero initial velocity?

        # concatenate all of the pieces
        pieces = []
        for segment in segments:
            pieces.extend(segment.pieces)

        # filter out zero-duration pieces and return
        pieces = [x for x in pieces if x.duration > EPS]
        return pieces

    def smooth(self, pieces):
        result = []
        for a, g in groupby(pieces, key=lambda x: x.acceleration):
            result.extend(self.smooth_group(list(g), a))
        return result

    def smooth_group(self, pieces, a):
        j = self.jerk
        t = sum(x.duration for x in pieces)
        vi = pieces[0].v1
        vf = pieces[-1].v2
        print a, len(pieces), vi, vf, t
        # /|___|\
        jf = 0.5
        t1 = t * j
        t2 = t * (1 - j)
        return pieces

# vf = vi + a * t
# s = (vf + vi) / 2 * t
# s = vi * t + a * t * t / 2
# vf * vf = vi * vi + 2 * a * s

def chop_piece(p, dt):
    result = []
    t = 0
    while t < p.duration:
        t1 = t
        t2 = min(t + dt, p.duration)
        p1 = p.point(t1)
        p2 = p.point(t2)
        v = (p.velocity(t1) + p.velocity(t2)) / 2
        result.append(Piece(p1, p2, v, 0, t2 - t1))
        t += dt
    return result

def chop_pieces(pieces, dt):
    result = []
    for piece in pieces:
        result.extend(chop_piece(piece, dt))
    return result
