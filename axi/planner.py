from __future__ import division

from bisect import bisect
from collections import namedtuple
from itertools import groupby
from math import sqrt, hypot
import numpy

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

def triangle(s, vi, vf, a, d, p1, p3):
    # compute a triangular profile: accelerating, decelerating
    s1 = (vf * vf - vi * vi - 2 * d * s) / (2 * a - 2 * d)
    s2 = s - s1
    vmax = (vi * vi + 2 * a * s1) ** 0.5
    t1 = (vmax - vi) / a
    t2 = (vf - vmax) / d
    p2 = p1.lerps(p3, s1)
    return Triangle(s1, s2, t1, t2, vmax, p1, p2, p3)

Trapezoid = namedtuple('Trapezoid',
    ['s1', 's2', 's3', 't1', 't2', 't3', 'p1', 'p2', 'p3', 'p4'])

def trapezoid(s, vi, vmax, vf, a, d, p1, p4):
    # compute a trapezoidal profile: accelerating, cruising, decelerating
    t1 = (vmax - vi) / a
    s1 = (vmax + vi) / 2 * t1
    t3 = (vf - vmax) / d
    s3 = (vf + vmax) / 2 * t3
    s2 = s - s1 - s3
    t2 = s2 / vmax
    p2 = p1.lerps(p4, s1)
    p3 = p1.lerps(p4, s - s3)
    return Trapezoid(s1, s2, s3, t1, t2, t3, p1, p2, p3, p4)

def acceleration_duration(s, vi, a):
    # compute the amount of time to travel distance s while accelerating
    vf = sqrt(vi * vi + 2 * a * s)
    t = (vf - vi) / a
    return t

def jerk_duration(s, vi, ai, j):
    # compute the amount of time to travel distance s while jerking
    # TODO: remove numpy dependency?
    roots = numpy.roots([j / 6, ai / 2, vi, -s])
    roots = roots.real[abs(roots.imag) < EPS]
    return float(min(x for x in roots if x > 0))

def jerk_factor(a, j, t):
    # compute a jerk factor based on desired jerk, 0 < jf <= 0.5
    a = abs(a)
    jt = j * t
    r = jt * (jt - 4 * a)
    if r < EPS:
        return 0.5
    return (jt - sqrt(r)) / (2 * jt)

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

Instant = namedtuple('Instant', ['t', 'p', 's', 'v', 'a', 'j'])

class Plan(object):
    # a complete motion profile
    def __init__(self, blocks):
        self.blocks = blocks
        self.duration = sum(b.t for b in blocks)
        self.length = sum(b.s for b in blocks)
        self.times = [] # start time of each block
        t = 0
        for b in blocks:
            self.times.append(t)
            t += b.t

    def instant(self, t):
        t = max(0, t)
        i = bisect(self.times, t) - 1
        b = self.blocks[i]
        bt = t - self.times[i]
        return b.instant(bt)

class Block(object):
    # a constant jerk for a duration of time
    def __init__(self, j, t, vi, ai, p1, p2):
        # TODO: track total time and distance for entire path or do in post?
        self.j = j
        self.t = t
        self.vi = vi
        self.ai = ai
        self.p1 = p1 # TODO: rename pi?
        self.p2 = p2 # TODO: rename pf?
        self.s = p1.distance(p2)
        # TODO: support providing vf, af when known
        self.vf = vi + ai * t + j * t * t / 2
        self.af = ai + j * t

    def split(self, t):
        x = self.instant(t)
        b1 = Block(self.j, t, self.vi, self.ai, self.p1, x.p)
        b2 = Block(self.j, self.t - t, x.v, x.a, x.p, self.p2)
        return b1, b2

    def instant(self, t):
        t2 = t * t
        t3 = t2 * t
        t2_2 = t2 / 2
        t3_6 = t3 / 6
        j = self.j
        a = self.ai + self.j * t
        v = self.vi + self.ai * t + self.j * t2_2
        s = self.vi * t + self.ai * t2_2 + self.j * t3_6
        p = self.p1.lerps(self.p2, s)
        return Instant(t, p, s, v, a, j)

def accelerate(segment, a, t, vi, p1, p2):
    if t < EPS:
        return
    segment.blocks.append(Block(0, t, vi, a, p1, p2))

class Segment(object):
    # a segment is a line segment between two points, which will be broken
    # up into blocks by the planner
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.length = p1.distance(p2)
        self.vector = p2.sub(p1).normalize()
        self.max_entry_velocity = 0
        self.entry_velocity = 0
        self.acceleration = 0
        self.deceleration = 0
        self.blocks = []

class Planner(object):
    def __init__(self, acceleration, max_velocity, corner_factor, jerk):
        self.acceleration = acceleration
        self.max_velocity = max_velocity
        self.corner_factor = corner_factor
        self.jerk = jerk

    def plan(self, points):
        j = self.jerk
        a = self.acceleration
        vmax = self.max_velocity
        cf = self.corner_factor
        return constant_acceleration_plan(points, j, a, vmax, cf)

    def jerk_plan(self, points):
        plan = self.plan(points)
        return constant_jerk_plan(plan, self.jerk)

def reverse_block_generator(segments, index):
    for i in range(index, -1, -1):
        for b in reversed(segments[i].blocks):
            yield i, b

def last_acceleration_group(segments, index):
    it = reverse_block_generator(segments, index)
    it = groupby(it, key=lambda (i, b): b.ai)
    try:
        it.next()
        a, g = it.next()
        blocks = list(g)
        t = sum(b.t for i, b in blocks)
        i = min(i for i, b in blocks)
        return i, a, t
    except StopIteration:
        return 0, 0, 0

def constant_acceleration_plan(points, j, amax, vmax, cf):
    # make sure points are Point objects
    points = [Point(x, y) for x, y in points]

    # create segments for each consecutive pair of points
    segments = [Segment(p1, p2) for p1, p2 in zip(points, points[1:])]

    # compute a max_entry_velocity for each segment
    # based on the angle formed by the two segments at the vertex
    for s1, s2 in zip(segments, segments[1:]):
        v = corner_velocity(s1, s2, vmax, amax, cf)
        s2.max_entry_velocity = v

    # add a dummy segment at the end to force a final velocity of zero
    segments.append(Segment(points[-1], points[-1]))

    # loop over segments
    i = 0
    # TODO: make jerk optional
    # return self.t >= 2 * self.a / self.j
    # segments[i].acceleration = amax
    # segments[i].deceleration = -amax
    a = amax
    d = -amax
    while i < len(segments) - 1:
        # pull out some variables
        segment = segments[i]
        next_segment = segments[i + 1]
        s = segment.length
        vi = segment.entry_velocity
        vexit = next_segment.max_entry_velocity
        p1 = segment.p1
        p2 = segment.p2
        # a = segments[i].acceleration
        # d = segments[i].deceleration
        # next_segment.acceleration = a
        # next_segment.deceleration = d

        # determine which profile to use for this segment
        # TODO: rearrange these cases for better flow?

        segment.blocks = []
        min_acceleration_time = 2 * a / j
        min_deceleration_time = 2 * d / -j

        gi, ga, gt = last_acceleration_group(segments, i)
        if ga < 0 and gt < min_deceleration_time:
            print gi, ga, gt, min_deceleration_time
            i = gi
            d = ga * 0.5
            continue
        if ga > 0 and gt < min_acceleration_time:
            print gi, ga, gt, min_acceleration_time
            i = gi
            a = ga * 0.5
            continue

        print i, a, d, min_acceleration_time, min_deceleration_time

        # accelerate? /
        vf = sqrt(vi * vi + 2 * a * s)
        if vf <= vexit:
            t = (vf - vi) / a
            accelerate(segment, a, t, vi, p1, p2)
            next_segment.entry_velocity = vf
            i += 1
            continue

        # accelerate, cruise, decelerate? /---\
        m = triangle(s, vi, vexit, a, d, p1, p2)
        if m.s1 > -EPS and m.s2 > -EPS and m.vmax >= vmax:
            raise
            z = trapezoid(s, vi, vmax, vexit, a, d, p1, p2)
            accelerate(segment, a, z.t1, vi, z.p1, z.p2)
            accelerate(segment, 0, z.t2, vmax, z.p2, z.p3)
            accelerate(segment, d, z.t3, vmax, z.p3, z.p4)
            next_segment.entry_velocity = vexit
            i += 1
            continue

        # accelerate, decelerate? /\
        if m.s1 > -EPS and m.s2 > -EPS:
            accelerate(segment, a, m.t1, vi, m.p1, m.p2)
            accelerate(segment, d, m.t2, m.vmax, m.p2, m.p3)
            next_segment.entry_velocity = vexit
            i += 1
            continue

        # too fast! update max_entry_velocity and backtrack
        segment.max_entry_velocity = sqrt(vexit * vexit + 2 * a * s)
        i -= 1 # TODO: support non-zero initial velocity?

    # concatenate all of the blocks
    blocks = []
    for segment in segments:
        blocks.extend(segment.blocks)

    # filter out zero-duration blocks and return
    # TODO: not needed anymore
    blocks = [b for b in blocks if b.t > EPS]
    return Plan(blocks)

def constant_jerk_plan(plan, j):
    # TODO: ignore blocks that already have a jerk?
    blocks = []
    for a, g in groupby(plan.blocks, key=lambda b: b.ai):
        blocks.extend(_constant_jerk_plan(list(g), j, a))
    return Plan(blocks)

def _constant_jerk_plan(blocks, j, a):
    if abs(a) < EPS:
        return blocks
    result = []
    duration = sum(b.t for b in blocks)
    jf = jerk_factor(a, j, duration)
    t1 = duration * jf
    t2 = duration - 2 * t1
    amax = a / (1 - jf)
    j = amax / t1 # actual jerk may exceed desired jerk
    vi = blocks[0].vi
    ai = 0
    s1 = vi * t1 + ai * t1 * t1 / 2 + j * t1 * t1 * t1 / 6
    v1 = vi + ai * t1 + j * t1 * t1 / 2
    s2 = v1 * t2 + amax * t2 * t2 / 2
    blocks1, temp = split_blocks(blocks, s1)
    blocks2, blocks3 = split_blocks(temp, s2)
    # jerk to a = amax
    for b in blocks1:
        t = jerk_duration(b.s, vi, ai, j)
        block = Block(j, t, vi, ai, b.p1, b.p2)
        result.append(block)
        vi = block.vf
        ai = block.af
    # accelerate at amax
    for b in blocks2:
        t = acceleration_duration(b.s, vi, ai)
        block = Block(0, t, vi, ai, b.p1, b.p2)
        result.append(block)
        vi = block.vf
        ai = block.af
    # jerk to a = 0
    for b in blocks3:
        t = jerk_duration(b.s, vi, ai, -j)
        block = Block(-j, t, vi, ai, b.p1, b.p2)
        result.append(block)
        vi = block.vf
        ai = block.af
    return result

def split_blocks(blocks, s):
    before = []
    after = []
    total = 0
    for b in blocks:
        s1 = total
        s2 = total + b.s
        if s2 < s + EPS:
            before.append(b)
        elif s1 > s - EPS:
            after.append(b)
        else:
            t = acceleration_duration(s - s1, b.vi, b.ai)
            b1, b2 = b.split(t)
            before.append(b1)
            after.append(b2)
        total = s2
    return before, after

# vf = vi + a * t
# s = (vf + vi) / 2 * t
# s = vi * t + a * t * t / 2
# vf * vf = vi * vi + 2 * a * s

# af = ai + j * t
# vf = vi + ai * t + j * t * t / 2
# sf = si + vi * t + ai * t * t / 2 + j * t * t * t / 6
