import json
import requests
import prcoords


class BaiduMap:
    def __init__(self, ak):
        self.ak = ak

    def _reqeustBaidu(self, url, **kwargs):
        kwargs.update({'ak': self.ak, 'output': 'json'})
        r = requests.get(url, params=kwargs)
        return_data = json.loads(r.text)

        if return_data['status']:
            message = return_data['message'] if return_data['message'] else 'error {:d}'.format(return_data['status'])
            raise BaiduAPIException(message)
        else:
            return return_data

    def coordinate(self, address):
        result = self._reqeustBaidu('http://api.map.baidu.com/geocoding/v3/',
                                    address=address)['result']

        lat, lng = prcoords.bd_wgs((result['location']['lat'],
                                    result['location']['lng']))

        confidence = [(100, 20), (90, 50), (80, 100), (75, 200), (70, 300), (60, 500),
                      (50, 1000), (40, 2000), (30, 5000), (25, 8000), (20, 10000)]
        precision = None
        for c in confidence:
            if result['confidence'] >= c[0]:
                precision = c[1]
                break
        return lat, lng, precision

    def address(self, lat, lng):
        result = self._reqeustBaidu('http://api.map.baidu.com/reverse_geocoding/v3/',
                                    location='{:f},{:f}'.format(lat, lng),
                                    coordtype='wgs84ll')
        return result['result']['formatted_address']

    def timezone(self, lat, lng):
        from time import time
        result = self._reqeustBaidu('http://api.map.baidu.com/timezone/v1',
                                    location='{:f},{:f}'.format(lat, lng),
                                    coordtype='wgs84ll',
                                    timestamp='{:d}'.format(int(time())))
        return (result['raw_offset'] + result['dst_offset']) / 3600

    def place_query(self, query, region):
        results = self._reqeustBaidu('http://api.map.baidu.com/place/v2/search',
                                     query=query, region=region,
                                     ret_coordtype='gcj02ll')['results']
        return [{
            'name': result['name'],
            'location': prcoords.gcj_wgs((result['location']['lat'],
                                          result['location']['lng']))
        } for result in results]


class BaiduAPIException(Exception):
    def __init__(self, msg):
        self.msg = msg
