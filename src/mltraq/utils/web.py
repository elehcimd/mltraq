import logging
import math
import os
import tempfile
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from tqdm.auto import tqdm
from urllib3.response import HTTPResponse

from mltraq.utils.bunch import Bunch

log = logging.getLogger(__name__)


class FileAdapter(HTTPAdapter):
    def send(self, request, *args, **kwargs):
        resp = HTTPResponse(body=open(request.url[7:], "rb"), status=200, preload_content=False)
        return self.build_response(request, resp)


def fetch(url: str, pathname: Optional[str] = None) -> Bunch:
    """
    Fetch URL with requests, saving it to `pathname` or a random one if not provided.

    The function returns a Bunch with attributes `url` with the input URL, `name` with
    the guessed name of the file, and `pathname` with the local saved copy pathname.

    If `pathname` is not provided, a temporary pathname is used.
    """

    meta = Bunch()
    meta.url = url
    meta.name = url.split("/")[-1] if "/" in url else None

    # Read a predefined number of bytes
    chunk_size = 8192
    # Set user agent to something less blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    # Wait for a response up to `timeout` seconds
    timeout = 10

    if pathname is None:
        from mltraq.storage.database import next_uuid

        pathname = tempfile.gettempdir() + os.sep + next_uuid().hex

    meta.pathname = pathname

    log.debug(f"Fetching file from {url} to {pathname}")

    s = requests.Session()
    s.mount("file://", FileAdapter())

    with s.get(url, stream=True, headers=headers, timeout=timeout) as r:
        r.raise_for_status()

        with open(pathname, "wb") as f:
            if "Content-length" in r.headers:
                content_length = int(r.headers["Content-length"])
                for chunk in tqdm(
                    r.iter_content(chunk_size=chunk_size), total=math.ceil(content_length / chunk_size), desc="Fetching"
                ):
                    f.write(chunk)
            else:
                f.write(r.content)

    return meta
