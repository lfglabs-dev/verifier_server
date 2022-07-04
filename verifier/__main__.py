from config import TomlConfig
from server.http import WebServer
from account.account import Account
from aiohttp import web
import logging
import asyncio


async def main():
    conf = TomlConfig("config.toml", "config.template.toml")
    account = Account(conf)
    await account.load()
    asyncio.create_task(start_server(conf, account))
    await asyncio.Event().wait()


async def start_server(conf, account):
    app = WebServer(conf, account).build_app()
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, port=conf.server_port).start()


logging.basicConfig(level=logging.INFO)
asyncio.run(main())
