import discord
import asyncio

from discord.ext import tasks
from WarningManager import Warning, WarningManager
from datetime import datetime, timezone

class AutoBrad(discord.Client):

    def __init__(self, warning_manager: WarningManager, *, intents: discord.Intents, **options) -> None:
        super().__init__(intents=intents, **options)

        self.thunderstorm_channel: discord.TextChannel = None
        self.tornado_channel: discord.TextChannel = None
        self.flood_channel: discord.TextChannel = None

        self.current_messages: set[discord.Message] = set()

        self.warning_manager = warning_manager

    async def on_ready(self) -> None:

        await self.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="Sniffing for warnings"))

        for channel in self.get_all_channels():
            if channel.type == discord.ChannelType.text:
                if channel.name == "autobrad-thunderstorm":
                    self.thunderstorm_channel = channel

                elif channel.name == "autobrad-tornado":
                    self.tornado_channel = channel

                elif channel.name == "autobrad-flood":
                    self.flood_channel = channel

        await self.thunderstorm_channel.purge()
        await self.tornado_channel.purge()
        await self.flood_channel.purge()

        await self.main_loop.start()

    @tasks.loop(minutes=3)
    async def main_loop(self) -> None:

        i = 0

        for warn in self.warning_manager.warning_set:

            if i == 5:
                await asyncio.sleep(1)

            message: discord.Embed = self.generate_warning_embed(warn)
            expiration_time: float = (warn.expiration_time - datetime.now(timezone.utc)).total_seconds()

            if "tornado" in warn.event_type.lower():
                await self.publish_warning(message, self.thunderstorm_channel, expiration_time)

            elif "thunderstorm" in warn.event_type.lower():
                await self.publish_warning(message, self.thunderstorm_channel, expiration_time)

            elif "flood" in warn.event_type.lower():
                await self.publish_warning(message, self.flood_channel, expiration_time)

            i += 1

    def generate_warning_embed(self, warning: Warning) -> discord.Embed:
        
        storm_info = [
        f"**Areas Listed:**",
        f"**Description:**",
        f"**Wind Gusts and Source:**",
        f"**Hail Size and Source:**",
        f"**Tornado Threat:**",
        f"Expires <t:{int(warning.expiration_time.timestamp())}:R>",
        ]

        message_content: list[str] = []

        for line, i in enumerate(storm_info, 0):

            if i == 0:
                message_content.append(f"{line} {warning.area_desc}")

            elif i == 1:
                message_content.append(f"{line} {warning.description}")
            
            if any(word in warning.event_type.lower() for word in ["tornado", "thunderstorm"]):
                if i == 2:
                    message_content.append(f"{line} {warning.wind_gust}/{warning.wind_threat}")

                elif i == 3:
                    message_content.append(f"{line} {warning.hail_size}/{warning.hail_threat}")

        content_string = '\n'.join(message_content)

        if "tornado" in warning.event_type.lower():
            embed_colour = discord.Color.red

        elif "thunderstorm" in warning.event_type.lower():
            embed_colour = discord.Color.yellow

        elif "flood" in warning.event_type.lower():
            embed_colour = discord.Color.green

        else:
            print(f"Unsupported Warning Type: {warning.event_type}")
            embed_colour = discord.Color.dark_grey

        return discord.Embed(colour=embed_colour, title=warning.headline, description=content_string)

    async def publish_warning(self, warning_message: discord.Embed, warning_channel: discord.TextChannel, expiration_time: float) -> dict:
        
        message = await warning_channel.send(warning_message)