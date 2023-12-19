def get_ip(request):
    #raw_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    # use 'HTTP_X_REAL_IP' according to PythonAnywhere
    # https://help.pythonanywhere.com/pages/WebAppClientIPAddresses
    raw_ip = request.META.get('HTTP_X_REAL_IP')
    if raw_ip is not None:
        # take the last ip on the list according to PythonAnywhere
        ip = raw_ip.split(',')[-1]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
