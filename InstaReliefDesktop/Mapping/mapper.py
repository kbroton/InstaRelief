from urllib import request
import urllib
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import cv2
import googlemaps
from math import log, exp, tan, atan, pi, ceil

EARTH_RADIUS = 6378137
EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0

def latlon_to_pixels(lat, lon, zoom):
    mx = (lon * ORIGIN_SHIFT) / 180.0
    my = log(tan((90 + lat) * pi/360.0))/(pi/180.0)
    my = (my * ORIGIN_SHIFT) /180.0
    res = INITIAL_RESOLUTION / (2**zoom)
    px = (mx + ORIGIN_SHIFT) / res
    py = (my + ORIGIN_SHIFT) / res
    return px, py


class Mapper(object):
    """
    This class holds the relevant information for
    the map.
    """
    def __init__(self, apikey):
        self.gmaps = googlemaps.Client(key=apikey)
        self.lat, self.lng = None, None
        self.zoom = 14
        self.width, self.height = 800, 800
        self.image = None
        self.scale = 1
        self.all_lat, self.all_lng = [], []
        self.color_type = {'Zombie': 'green', 'Water': 'blue', 'Fire': 'red',
                           'Tornado': 'brown'}

    def geocode(self, addresses, cities):
        state = 'CA'
        for address, city in zip(addresses, cities):
            location = address + ', ' + city + ', ' + state
            result = self.gmaps.geocode(location)[0]
            self.lat = result['geometry']['location']['lat']
            self.lng = result['geometry']['location']['lng']
            self.all_lat.append(self.lat)
            self.all_lng.append(self.lng)

    def download_image(self, types):
        markers_list = []
        for i in range(len(self.all_lng)):
            lng = self.all_lng[i]
            lat = self.all_lat[i]
            type = types[i]
            marker = '&markers=color:'+self.color_type[type]+'%7Clabel:S%7C' + str(lat) + ',' + str(lng)
            markers_list.append(marker)

        urlparams = 'center='+str(self.lat)+','+str(self.lng)+'&size='+str(self.width)+'x'+str(self.height)+'&zoom='+str(self.zoom)+'&sensor=false'
        url = 'http://maps.googleapis.com/maps/api/staticmap?' + urlparams
        for marker in markers_list:
            url += marker

        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype='uint8')
        self.image = cv2.imdecode(image, 1)


if __name__ == '__main__':
    mapper = Mapper('AIzaSyDW6MkN0YmFQd2m3XD7ySG0GbsqcQDd5TE')
    address = '1 Space Park Blvd'
    city = 'Redondo Beach'
    state = 'CA'
    mapper.geocode(address, city, state)
    mapper.download_image()
