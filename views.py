from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseNotAllowed
from django.core.validators import FileExtensionValidator
from django.http.request import MultiPartParser
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse, parse_qs
import os
import requests
import json

from django.shortcuts import render

from helpers.cookie_set_get import set_cookie, get_cookie
from helpers.headers_set_get import get_header, set_header

def read_entities():
    f = os.path.join(os.path.dirname(__file__), 'data/entities.txt')
    with open(f, 'r') as fl:
        entities = json.load(fl)
    return entities

def write_entities(entities):
    f = os.path.join(os.path.dirname(__file__), 'data/entities.txt')
    with open(f, 'w') as fl:
        json.dump(entities, fl, indent=0)

def show_top_nbu_rates(request):
    rates = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
    rateDict = rates.json()
    responseList: list = []
    for i in sorted(rateDict, key=lambda d: d['rate'], reverse=True)[0:10]:
        responseList.append(i)

    return HttpResponse(content=json.dumps(responseList), content_type="application/json")

""" ------------ HW 3 BEGIN --------------- """

@csrf_exempt
def show_image(request, imagepth):
    if request.method == "GET":
        img_path = os.path.join("./assets", imagepth)
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
        return HttpResponseNotAllowed(permitted_methods=["GET"])
    
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
        return HttpResponseNotAllowed(permitted_methods=["POST"])
    
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
        return HttpResponseNotAllowed(permitted_methods=["POST"])

""" ------------ HW 3 END --------------- """


""" ------------ HW 6 BEGIN --------------- """

def entity_list(request):
    entities = read_entities()
    return render(request, 'entity_list.html', {'entities': entities})

def entity_detail(request, id):
    """ localhost:8000/entity/ """

    entities = read_entities()
    for entity in entities:
        if entity['id'] == id:
            return render(request, 'entity_detail.html', {'entity': entity})
    
    return HttpResponseNotFound(content=json.dumps({"msg": "entity not found"}), content_type="application/json")

@csrf_exempt
def create_entity(request):
    """ localhost:8000/entity/create/ \n""" \
    """ body : {"id":1,"name":"dummy2","img_link":"netflix_image.png"}"""

    if request.method == 'POST':
        try:
            dt = json.loads(request.body)
            entities = read_entities()
            entities.append(dt)
            write_entities(entities)
            return HttpResponse(content=json.dumps({"msg": "create success"}), content_type="application/json")
        except Exception as e:
            return HttpResponse(content=json.dumps({"msg": "error creating"}), status=500, content_type="application/json")
    else:
        return HttpResponseNotAllowed(permitted_methods=["POST"], content=json.dumps({"msg": "method not allowed"}))

@csrf_exempt
def delete_entity(request, id):
    """ localhost:8000/entity/<ID>/delete/ """

    if request.method == 'DELETE':
        try:
            entities = read_entities()
            entities = [e for e in entities if e.get('id') != int(id)]
            write_entities(entities)
            return HttpResponse(content=json.dumps({"msg": "delete success"}), content_type="application/json")
        except Exception as e:
            return HttpResponse(content=json.dumps({"msg": "error deleting"}), status=500, content_type="application/json")
    else:
        return HttpResponseNotAllowed(permitted_methods=["DELETE"], content=json.dumps({"msg": "method not allowed"}))
    
""" ------------ HW 6 END --------------- """


""" ------------ HW 7 BEGIN --------------- """

@csrf_exempt
def set_cookie_view(request):
    """ localhost:8000/cookie/set/?n=dummy&val=dummy_value&httpOnly=false"""

    if request.method == 'GET':
        response = HttpResponse(content=json.dumps({'msg': 'set success'}), content_type="application/json")
        set_cookie(response, request.GET.get('n'), request.GET.get('val'), request.GET.get('httpOnly', False) == 'true')
        return response
    
    return HttpResponseNotAllowed(permitted_methods=["GET"], content=json.dumps({"msg": "method not allowed"}))

@csrf_exempt
def get_cookie_view(request, n):
    """ localhost:8000/cookie/get/dummy """

    if request.method == 'GET':
        return HttpResponse(content=json.dumps({n: get_cookie(request, n)}), content_type="application/json")
    
    return HttpResponseNotAllowed(permitted_methods=["GET"], content=json.dumps({"msg": "method not allowed"}))

@csrf_exempt
def set_header_view(request):
    """ localhost:8000/header/set/?n=dummy&val=dummy_val """
    
    if request.method == 'GET':
        response = HttpResponse(content=json.dumps({'msg': 'set success'}), content_type="application/json")
        set_header(response, request.GET.get('n'), request.GET.get('val'))
        return response

    return HttpResponseNotAllowed(permitted_methods=["GET"], content=json.dumps({"msg": "method not allowed"}))

@csrf_exempt
def get_header_view(request, n):
    """ localhost:8000/header/get/dummy \n""" \
    """ in headers set dummy:<some value> """

    if request.method == 'GET':
        return HttpResponse(content=json.dumps({n: get_header(request, n)}), content_type="application/json")
    
    return HttpResponseNotAllowed(permitted_methods=["GET"], content=json.dumps({"msg": "method not allowed"}))

""" ------------ HW 7 END --------------- """

def info(request):
    return HttpResponse(content=json.dumps(
        {"info": "file upload can be used via /metadata/, use form-data to attach file and search string to find\n \
         url validation can be accesed via /url_validate/ and body parameter 'url'\nand lastly image can be accessed through /image/\n \
         /entity/ to list entities\n/entity/<ID>/ to check detailed entity\n/entity/create/ to create entity, pass it as raw body json object in post\n/entity/<ID>/delete/ to delete entity"}), content_type="application/json")
