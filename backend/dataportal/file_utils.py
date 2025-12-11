from pathlib import Path
from typing import Dict, List, Tuple, Union

from django.conf import settings
from django.http import FileResponse, HttpResponse


def get_file_list(path: str, recursive: bool = False) -> Tuple[bool, Union[List[Dict], str]]:
    """
    Get a list of files from the mounted data directory

    :param path: The relative path to list files from
    :param recursive: Whether to list files recursively
    :return: Tuple (success: bool, result: List[Dict] or error message)
    """
    base_dir = Path(settings.MEERTIME_DATA_DIR)
    full_path = base_dir / path.lstrip("/")

    try:
        if not full_path.exists():
            return False, f"Path not found: {path}"

        if not full_path.is_dir():
            return False, f"Path is not a directory: {path}"

        result = []

        if recursive:
            for file_path in full_path.glob("**/*"):
                if file_path.is_file():
                    # Get the relative path from base directory
                    rel_path = file_path.relative_to(base_dir)
                    result.append(
                        {
                            "path": f"/{rel_path}",
                            "fileName": file_path.name,
                            "fileSize": file_path.stat().st_size,
                            "isDirectory": False,
                        }
                    )
        else:
            for item_path in full_path.iterdir():
                # Get the relative path from base directory
                rel_path = item_path.relative_to(base_dir)
                is_dir = item_path.is_dir()
                result.append(
                    {
                        "path": f"/{rel_path}",
                        "fileName": item_path.name,
                        "fileSize": 0 if is_dir else item_path.stat().st_size,
                        "isDirectory": is_dir,
                    }
                )

        return True, result
    except Exception as e:
        return False, f"Error listing files: {str(e)}"


def get_file_path(path: str) -> Tuple[bool, Union[Path, str]]:
    """
    Validate and return the full filesystem path for a file

    :param path: The relative path to the file
    :return: Tuple (success: bool, full_path: Path or error message)
    """
    base_dir = Path(settings.MEERTIME_DATA_DIR)
    full_path = base_dir / path.lstrip("/")

    try:
        if not full_path.exists():
            return False, f"File not found: {path}"

        if not full_path.is_file():
            return False, f"Path is not a file: {path}"

        # Ensure the path is within the allowed directory by resolving symlinks
        # Resolve both paths to handle symlinks consistently
        real_path = full_path.resolve()
        real_base_dir = base_dir.resolve()
        if not str(real_path).startswith(str(real_base_dir)):
            return False, "Access denied: Path outside of allowed directory"

        return True, full_path
    except Exception as e:
        return False, f"Error accessing file: {str(e)}"


def serve_file(path: str) -> HttpResponse:
    """
    Serve a file from the mounted data directory

    :param path: The relative path to the file
    :return: FileResponse or error response
    """
    success, result = get_file_path(path)

    if not success:
        return HttpResponse(result, status=404)

    try:
        return FileResponse(result.open("rb"), filename=result.name, as_attachment=True)
    except Exception as e:
        return HttpResponse(f"Error serving file: {str(e)}", status=500)
