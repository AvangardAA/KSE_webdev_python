def set_header(response, n, val):
    response[n] = val

def get_header(request, n):
    return request.headers.get(n, 'not found')