import aiohttp
from .common import WrongRequestException


async def start_twitter(conf, code):

    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            conf.twitter_api_endpoint + "/oauth2/token",
            data={
                "code": code,
                "grant_type": "authorization_code",
                "client_id": conf.twitter_client_id,
                "redirect_uri": "https://goerli.app.starknet.id/twitter",
                "code_verifier": "challenge",
                "scope": "identify",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status != 200:
            raise WrongRequestException()

        content = await resp.json()
        token_type = content["token_type"]
        token = content["access_token"]

        resp = await session.get(
            "https://api.twitter.com/2/users/me",
            headers={"Authorization": f"{token_type} {token}"},
        )
        if resp.status != 200:
            raise WrongRequestException()
        content = await resp.json()
        data = content["data"]
        user_id = data["id"]
        name = data["name"]
        username = data["username"]

        return user_id, username, name
