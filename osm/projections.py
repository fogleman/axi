from __future__ import division

from math import *

EARTH_RADIUS_KM = 6371

def haversine(lat1, lng1, lat2, lng2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    return asin(sqrt(a)) * 2 * EARTH_RADIUS_KM

def kilometer_scale(projection, lng, lat):
    km = 1
    dlng = degrees(2 * asin(sin(km / (2 * EARTH_RADIUS_KM)) / cos(radians(lat))))
    x1, _ = projection.project(lng, lat, False)
    x2, _ = projection.project(lng + dlng, lat, False)
    return 1 / abs(x2 - x1)

class LambertAzimuthalEqualArea(object):
    def __init__(self, lng, lat, rotation_degrees=0):
        self.lng = lng
        self.lat = lat
        self.cos = cos(radians(rotation_degrees))
        self.sin = sin(radians(rotation_degrees))
        self.scale = kilometer_scale(self, lng, lat)
    def project(self, lng, lat, scale_and_rotate=True):
        lng, lat = radians(lng), radians(lat)
        clng, clat = radians(self.lng), radians(self.lat)
        k = sqrt(2 / (1 + sin(clat)*sin(lat) + cos(clat)*cos(lat)*cos(lng-clng)))
        x = k * cos(lat) * sin(lng-clng)
        y = k * (cos(clat)*sin(lat) - sin(clat)*cos(lat)*cos(lng-clng))
        if scale_and_rotate:
            s = self.scale
            tx = x * self.cos - y * self.sin
            ty = y * self.cos + x * self.sin
            x = tx * s
            y = ty * s
        return (x, -y)
