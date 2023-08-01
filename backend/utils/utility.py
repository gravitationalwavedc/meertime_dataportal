import os
import jwt
import base64

from django.http import HttpResponse
from django.conf import settings


def secure_serve(request, document_root=None, show_indexes=False, *args, **kwargs):
    """
    function to return the base64 of the image if a valid jwt token is supplied
    otherwise - it will return an empty string, meaning no media file.
    """
    try:
        token = request.META["HTTP_AUTHORIZATION"].split(" ")[-1]
        # expired token for test
        # token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNzYWxlaGVlbkBzd2luLmVkdS5hdSIsImV4cCI6MTY4NjE5MTg4Niwib3JpZ0lhdCI6MTY4NjE5MTU4Nn0.dRxwWuQ2PAH3fGQhkCKjjtl-3_9c63zkcuCmuZd5oig'
        jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        file_path = request.path.replace("/media/", "")
        image_file = os.path.join(document_root, file_path)
        with open(image_file, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())
        return HttpResponse(b64_string)
    except Exception as ex:
        print(ex)
        return HttpResponse("")
