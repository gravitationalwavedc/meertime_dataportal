import base64
import os

from django.http import HttpResponse


def secure_serve(request, document_root=None, show_indexes=False, *args, **kwargs):
    """
    function to return the base64 of the image if the user is authenticated
    otherwise - it will return a 401 Unauthorized response.
    """
    # Check if the user is authenticated through Django's session
    if not request.user.is_authenticated:
        return HttpResponse("Authentication required", status=401)

    try:
        file_path = request.path.replace("/media/", "")
        image_file = os.path.join(document_root, file_path)
        with open(image_file, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())
        return HttpResponse(b64_string)
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)
    except Exception as ex:
        print(f"Error serving file: {ex}")
        return HttpResponse("Server error", status=500)
