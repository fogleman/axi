from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_KM = 6371

def haversine(lat1, lng1, lat2, lng2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    return asin(sqrt(a)) * 2 * EARTH_RADIUS_KM

class LambertAzimuthalEqualArea(object):
    def __init__(self, lng, lat, rotation_degrees=0):
        self.lng = lng
        self.lat = lat
        self.cos = cos(radians(rotation_degrees))
        self.sin = sin(radians(rotation_degrees))
        self.scale = 1
        self.scale = self.kilometer_scale()
    def project(self, lng, lat):
        lng, lat = radians(lng), radians(lat)
        clng, clat = radians(self.lng), radians(self.lat)
        k = sqrt(2 / (1 + sin(clat)*sin(lat) + cos(clat)*cos(lat)*cos(lng-clng)))
        x = k * cos(lat) * sin(lng-clng)
        y = k * (cos(clat)*sin(lat) - sin(clat)*cos(lat)*cos(lng-clng))
        s = self.scale
        rx = x * self.cos - y * self.sin
        ry = y * self.cos + x * self.sin
        return (rx * s, -ry * s)
    def kilometer_scale(self):
        e = 1e-3
        lng, lat = self.lng, self.lat
        km_per_lng = haversine(lat, lng - e, lat, lng + e) / (2 * e)
        km_per_lat = haversine(lat - e, lng, lat + e, lng) / (2 * e)
        x1, y1 = self.project(lat - 1 / km_per_lat, lng - 1 / km_per_lng)
        x2, y2 = self.project(lat + 1 / km_per_lat, lng + 1 / km_per_lng)
        sx = 2 / (x2 - x1)
        sy = 2 / (y1 - y2)
        return (sx + sy) / 2
