def set_cookie(response, n, val, httpO):
    response.set_cookie(n, val, httponly=httpO)

def get_cookie(request, n):
    return request.COOKIES.get(n, 'not found')