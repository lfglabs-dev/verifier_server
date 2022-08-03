from config import TomlConfig
from server.http import WebServer
from aiohttp import web
import logging
import asyncio


async def main():
    conf = TomlConfig("config.toml", "config.template.toml")
    asyncio.create_task(start_server(conf))
    await asyncio.Event().wait()


async def start_server(conf):
    app = WebServer(conf).build_app()
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, port=conf.server_port).start()


logging.basicConfig(level=logging.INFO)
asyncio.run(main())
