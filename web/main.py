from typing import List, Dict, Callable, Union
from aiohttp import web


class WebServer:
    def __init__(self) -> None:
        self.app = web.Application()

    def add_route(self, routes: List[Dict[str, Union[str, Callable]]]) -> None:
        _routes = []

        for route in routes:
            handler: Callable = route["handler"]
            path: str = route["path"]

            if route["method"].lower() == "get":
                _routes.append(web.get(path, handler))

            elif route["method"].lower() == "post":
                _routes.append(web.post(path, handler))

        self.app.add_routes(_routes)

    def run(self):
        web.run_app(self.app)


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


server = WebServer()
server.add_route([
    {"path": "/command", "method": "GET", "handler": handle}
])
server.run()
