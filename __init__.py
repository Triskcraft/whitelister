import asyncio
import discord
from discord import app_commands, Member
from discord.ext import commands
from mcdis_rcon.utils import isAdmin, mc_uuid
from mcdis_rcon.classes import McDisClient

class WhiteList(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client
        self.interviewer_id = 1355617895480164472

    @app_commands.command(name="whitelist", description="Gestiona la whitelist del servidor")
    @app_commands.describe(action="Acción a realizar", nickname="Nombre del jugador")
    async def whitelist(self, interaction: discord.Interaction, action: str, nickname: str):
        member = interaction.user
        assert self.client.user
        if not isinstance(member, Member): return
        if not isAdmin(member) and self.interviewer_id not in [r.id for r in getattr(member, 'roles', [])]:
            await interaction.response.send_message("✖ No tienes permisos.", ephemeral=True)
            return

        action = action.lower()
        if action not in ["add", "remove"]:
            await interaction.response.send_message("✖ Acción no válida. Usa `add` o `remove`.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        try:
            network_server = next((s for s in self.client.servers if s.name.lower() == "network"), None)
            if not network_server:
                await interaction.followup.send("✖ No se encontró el servidor 'Network'.")
                return
            network_server.process
            uuid = mc_uuid(nickname)
            uuid_text = uuid if uuid else "UUID no encontrado"

            network_server.execute(f"vcl {action} {nickname}")

            content = "✅ Usuario añadido a la whitelist." if action == "add" else "✅ Usuario removido de la whitelist."

            embed = discord.Embed(
                title="> **Whitelist TriskCraft**",
                description=f"{content}\n- **Username:** {nickname}\n- **UUID:** `{uuid_text}`",
                color=0x2f3136
            ).set_thumbnail(
                url=f"https://mc-heads.net/head/{nickname.lower()}.png"
            ).set_footer(
                text='Whitelist System \u200b',
                icon_url=self.client.user.display_avatar.url
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @whitelist.autocomplete("action")
    async def action_autocomplete(self, interaction: discord.Interaction, current: str):
        options = ["add", "remove"]
        return [
            app_commands.Choice(name=opt, value=opt)
            for opt in options if current.lower() in opt
        ][:5]

class mdaddon(commands.Cog):
    def __init__(self, client: McDisClient):
        asyncio.create_task(client.add_cog(WhiteList(client)))