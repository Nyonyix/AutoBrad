import discord
from discord.ext import tasks

class AutoBrad(discord.Client):

    def __init__(self, *, intents: discord.Intents, **options) -> None:
        super().__init__(intents=intents, **options)

    async def on_ready(self) -> None:

        thunderstorm_channel: discord.TextChannel
        tornado_channel: discord.TextChannel
        flood_channel: discord.TextChannel

        await self.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="Sniffing for warnings"))

        for channel in self.get_all_channels():
            if channel.type == discord.ChannelType.text:
                if channel.name == "autobrad-thunderstorm":
                    thunderstorm_channel = channel
                elif channel.name == "autobrad-tornado":
                    tornado_channel = channel
                elif channel.name == "autobrad-flood":
                    flood_channel = channel

        await thunderstorm_channel.purge()
        await tornado_channel.purge()
        await flood_channel.purge()

    tasks.loop(minutes=3)
    async def main_loop(self) -> None:
        pass

    async def format_warnings(self, warning_type: str) -> None:
        pass

    async def publish_warnings(self, warning_type: str) -> None:
        pass