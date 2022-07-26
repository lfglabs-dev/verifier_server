from verifications.discord import start_discord
from verifications.twitter import start_twitter
from account.account import assert_id
from aiohttp import web
import aiohttp_cors
import asyncio


class WebServer:
    def __init__(self, conf, account) -> None:
        self.conf = conf
        self.account = account
        self.tokens = {}

    async def remove_token(self, reference):
        await asyncio.sleep(60 * 30)
        if reference in self.tokens:
            del self.tokens[reference]

    async def start_process(self, request):
        params = await request.json()

        reference = params["reference"]
        if len(reference) > 32:
            return web.json_response({"status": "error", "error": "invalid reference"})

        type = params["type"]
        if type not in ["discord", "twitter"]:
            print(type)
            return web.json_response({"status": "error", "error": "invalid type"})

        if type == "discord":
            code = params["code"]
            try:
                user_id, username, discriminator = await start_discord(self.conf, code)
            except Exception:
                return web.json_response(
                    {"status": "error", "error": "unable to query discord data"}
                )
            self.tokens[reference] = int(user_id)
            asyncio.create_task(self.remove_token(reference))

            return web.json_response(
                {
                    "status": "success",
                    "id": user_id,
                    "username": username,
                    "discriminator": discriminator,
                }
            )

        if type == "twitter":
            code = params["code"]
            try:
                user_id, username, name = await start_twitter(self.conf, code)
                print(user_id, username, name)
            except Exception:
                return web.json_response(
                    {"status": "error", "error": "unable to query twitter data"}
                )
            self.tokens[reference] = int(user_id)
            asyncio.create_task(self.remove_token(reference))

            return web.json_response(
                {
                    "status": "success",
                    "id": user_id,
                    "username": username,
                    "name": name,
                }
            )

        return web.json_response({"status": "error", "error": "invalid type"})

    async def verify(self, request):
        params = await request.json()
        try:
            type = params["type"]
            if type not in ["discord"]:
                return web.json_response({"status": "error", "error": "invalid type"})
            nftid = params["nftid"]

            try:
                if type == "discord":
                    reference = params["reference"]
                    user_id = self.tokens[reference]
                    await assert_id(self.account, nftid, type, user_id)
                    txid = await self.account.confirm_validity(nftid, type, user_id)
                else:
                    txid = 0
            except Exception:
                return web.json_response({"status": "error", "error": "invalid proof"})

            return web.json_response({"status": "success", "txid": txid})

        except KeyError:
            return web.json_response({"status": "error", "error": "invalid request"})

    def build_app(self):
        app = web.Application()
        app.add_routes([web.post("/start_process", self.start_process)])
        app.add_routes([web.post("/verify", self.verify)])
        cors = aiohttp_cors.setup(
            app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                )
            },
        )
        for route in list(app.router.routes()):
            cors.add(route)
        return app
