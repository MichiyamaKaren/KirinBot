def weatherAPI(lat, lon, ac=0, tzshift=0):
    url = 'http://7timer.cn/index.php'
    parameters = dict(product='civil', lat=lat, lon=lon, ac=ac, tzshift=tzshift, lang='zh-CN', unit='metric')
    return url + '?' + '&'.join([key + '=' + str(value) for key, value in parameters.items()])
