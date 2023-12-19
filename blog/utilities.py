def get_ip(request):
    #raw_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    raw_ip = request.META.get('HTTP_X_REAL_IP')
    if raw_ip is not None:
        ip = raw_ip.split(',')[-1]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
