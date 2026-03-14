import asyncio
from mcdis_rcon.classes import McDisClient


class mdaddon():
    def __init__(self, client: McDisClient):
        asyncio.create_task(client.load_extension('Commands.whitelist'))