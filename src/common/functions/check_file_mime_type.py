import magic
from pathlib import Path


def is_file_mime_type_correct(buffer: bytes, file_name: str) -> str:
    """
    Check the MIME type of file using python-magic.
    :param buffer: The file content as bytes.
    :param file_name: The file name.
    :return: MIME type of the file.
    """
    allowed_extensions: tuple = ("jpg", "jpeg", "png", "webp")

    file_ext: str = Path(file_name).suffix.lower()[1:]  # Remove the dot from the extension
    file_ext = "jpeg" if file_ext == "jpg" else file_ext
    mime_type: str = magic.from_buffer(buffer, mime=True)

    # image/jpeg -> jpeg
    real_ext: str = mime_type.split("/")[1]
    if real_ext == file_ext and real_ext in allowed_extensions:
        return mime_type
    else:
        raise ValueError(f"Invalid file type: {mime_type}. Expected image file with extensions {allowed_extensions}.")