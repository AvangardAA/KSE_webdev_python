from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseNotAllowed
from django.core.validators import FileExtensionValidator
from django.http.request import MultiPartParser
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse, parse_qs
import os
import requests
import json

def show_top_nbu_rates(request):
    rates = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
    rateDict = rates.json()
    responseList: list = []
    for i in sorted(rateDict, key=lambda d: d['rate'], reverse=True)[0:10]:
        responseList.append(i)

    return HttpResponse(content=json.dumps(responseList), content_type="application/json")

@csrf_exempt
def show_image(request, imagepth):
    if request.method == "GET":
        img_path = os.path.join("../assets", imagepth)
        if os.path.exists(img_path) and os.path.isfile(img_path):
            with open(img_path, 'rb') as fl:
                img_send = fl.read()

            content_map = {
                '.png': 'image/png',
                '.jpeg': 'image/jpeg',
                '.jpg': 'image/jpeg',
            }
            _, ext = os.path.splitext(img_path)
            content_type = content_map.get(ext, 'application/octet-stream')

            return HttpResponse(img_send, content_type=content_type)
        else:
            return HttpResponseNotFound(json.dumps({"error": "image not found"}), content_type="application/json")
    else:
        return HttpResponseNotAllowed(permitted_methods=["POST", "PUT", "DELETE", "PATCH"])
    
@csrf_exempt
def url_validate(request):
    """ Send url as json encoded object : {"url": "..."}
        Example of working string is {"url": "https://dummy.com/dummy1/dummy2?param1=1&param2=2"}
    """
    if request.method == "POST":
        try:
            url = json.loads(request.body)
            p_url = urlparse(url["url"])

            protocol = p_url.scheme
            domain = p_url.netloc
            path_steps = p_url.path.strip('/').split('/')
            query_params = parse_qs(p_url.query)

            if protocol not in ["http", "https", "ftp"]:
                return HttpResponseBadRequest(content=json.dumps({"error": "invalid protocol"}), content_type="application/json")
            elif domain == "":
                return HttpResponseBadRequest(content=json.dumps({"error": "cant resolve domain"}), content_type="application/json")
            elif path_steps == []:
                return HttpResponseBadRequest(content=json.dumps({"error": "empty path steps"}), content_type="application/json")
            elif query_params == {}:
                return HttpResponseBadRequest(content=json.dumps({"error": "empty query params"}), content_type="application/json")
            else:
                return HttpResponse(content=json.dumps({
                    'done': {
                        'protocol': protocol,
                        'domain': domain,
                        'path_steps': path_steps,
                        'query_params': query_params,
                    }
                }), content_type="application/json")
        
        except Exception as e:
            return HttpResponseBadRequest(content=json.dumps({"error": "something wrong with request body"}), content_type="application/json")
    else:
        return HttpResponseNotAllowed(permitted_methods=["GET", "PUT", "DELETE", "PATCH"])
    
@csrf_exempt
def metadata_text(request):
    """ In order to use this send file and search string in body as form-data """
    if request.method == 'POST':
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        post, flbuf = parser.parse()

        fl = flbuf.get('file')
        FileExtensionValidator(allowed_extensions=['txt'])(fl)
        ftext = fl.read().decode('utf-8')
        search = post.get('search', '')

        return HttpResponse(content=json.dumps({
            'length': len(ftext),
            'alphas': sum(c.isalnum() for c in ftext),
            'occurrences': ftext.lower().count(search.lower()),
        }), content_type="application/json")
    else:
        return HttpResponseNotAllowed(permitted_methods=["GET", "PUT", "DELETE", "PATCH"])
    
def info(request):
    return HttpResponse(content=json.dumps(
        {"info": "file upload can be used via /metadata/, use form-data to attach file and search string to find\nurl validation can be accesed via /url_validate/ and body parameter 'url'\nand lastly image can be accessed through /image/"}), content_type="application/json")
