#!/usr/bin/env python3
from aiohttp import web
import asyncio
import os


class TarpitServer:
    FLOOD_CHUNK_SIZE = 1024 * 1024  # 1MB

    def __init__(self, address="0.0.0.0", port=8080):
        self.address = address
        self.port = port
        self.app = web.Application()
        self.app.router.add_get("/", self.serve_index)
        self.app.router.add_get("/tarpit", self.serve_tarpit)
        self.app.router.add_get("/cat.jpg", self.serve_cat)

        """ 
        Some consistent data to make the tarpit look like an enormous HTML page with obfuscated code.
        Based on https://www.akamai.com/blog/security/catch-me-if-you-can-javascript-obfuscation
        """
        html_start = ("<!DOCTYPE html><html lang=\"en\"><head><script "
                      "type=\"text/javascript\">window.location=\"data:text/html;base64,")
        self.__html_start = html_start.encode("utf-8")

    async def serve_index(self, request):
        return web.FileResponse("./index.html")

    async def serve_cat(self, request):
        return web.FileResponse("cat.jpg")

    async def serve_tarpit(self, request):
        try:
            response = web.StreamResponse(
                headers={"Content-Type": "text/html", "Server": "TarpitServer"}
            )
            response.enable_chunked_encoding()
            await response.prepare(request)
            await response.write(self.__html_start)
            while True:
                data = os.urandom(self.FLOOD_CHUNK_SIZE)
                await response.write(data)
                await asyncio.sleep(0.0001)  # Allow event loop to handle other tasks
        except ConnectionError or ConnectionAbortedError or Exception:
            ...
        return

    def run(self):
        web.run_app(self.app, host=self.address, port=self.port)


if __name__ == "__main__":
    server = TarpitServer()
    server.run()
