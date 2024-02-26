import base64
import os

import jwt
from django.conf import settings
from django.http import HttpResponse


def secure_serve(request, document_root=None, show_indexes=False, *args, **kwargs):
    """
    function to return the base64 of the image if a valid jwt token is supplied
    otherwise - it will return an empty string, meaning no media file.
    """
    try:
        token = request.META["HTTP_AUTHORIZATION"].split(" ")[-1]
        jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        file_path = request.path.replace("/media/", "")
        image_file = os.path.join(document_root, file_path)
        with open(image_file, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())
        return HttpResponse(b64_string)
    except Exception as ex:
        print(ex)
        return HttpResponse("")
