import httpx

client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    global client
    if client is None or client.is_closed:
        client = httpx.AsyncClient(timeout=15.0)
    return client
