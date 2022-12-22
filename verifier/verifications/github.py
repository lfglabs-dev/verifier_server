import aiohttp
from .common import WrongRequestException


async def start_github(conf, code):

    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            conf.github_api_endpoint + "/oauth/access_token",
            data={
                "code": code,
                "client_id": conf.github_client_id,
                "client_secret": conf.github_client_secret,
                "redirect_uri": "https://goerli.app.starknet.id/github",
            },
            headers={"Accept": "application/json"},
        )
        if resp.status != 200:
            raise WrongRequestException()
 
        content = await resp.json()
        token_type = content["token_type"]
        token = content["access_token"]

        resp = await session.get(
            "https://api.github.com/user",
            headers={"Authorization": f"{token_type} {token}"},
        )
        if resp.status != 200:
            raise WrongRequestException()

        content = await resp.json()
        user_id = content["id"]
        username = content["login"]
        name = content["name"]

        return user_id, username, name
