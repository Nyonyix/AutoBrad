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

        self.current_messages: dict[Warning, discord.Message] = {}

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

        self.warning_manager.update()
        i = 0

        messages_to_remove = []
        for k, v in self.current_messages.items():
            if k not in self.warning_manager.warning_set:
                await v.delete()
                messages_to_remove.append(k)

        for m in messages_to_remove:
            self.current_messages.pop(m)

        for warn in self.warning_manager.warning_set:

            if warn not in self.current_messages.keys():

                if i == 5:
                    await asyncio.sleep(1)

                message_embed: discord.Embed = self.generate_warning_embed(warn)
                expiration_time: float = (warn.expiration_time - datetime.now(timezone.utc)).total_seconds()

                if "tornado" in warn.event_type.lower():
                    message = await self.tornado_channel.send(embed=message_embed, delete_after=expiration_time)

                elif "thunderstorm" in warn.event_type.lower():
                    message = await self.thunderstorm_channel.send(embed=message_embed, delete_after=expiration_time)

                elif "flood" in warn.event_type.lower():
                    message = await self.flood_channel.send(embed=message_embed, delete_after=expiration_time)

                self.current_messages[warn] = message

                i += 1

    def generate_warning_embed(self, warning: Warning) -> discord.Embed:
        
        storm_info = [
        f"**Areas Listed:**",
        f"**Description:**",
        f"**Wind Gusts and Source:**",
        f"**Hail Size and Source:**",
        f"**Tornado Threat:**",
        f"**Expires** <t:{int(warning.expiration_time.timestamp())}:R>",
        ]

        message_content: list[str] = []

        for i, line in enumerate(storm_info):

            if i == 0:
                message_content.append(f"{line} {warning.area_desc}")

            elif i == 1:
                message_content.append(f"{line} {warning.description}")
            
            if any(word in warning.event_type.lower() for word in ["tornado", "thunderstorm"]):
                if i == 2:
                    message_content.append(f"{line} {warning.wind_gust} and is {warning.wind_threat}")

                elif i == 3:
                    message_content.append(f"{line} {warning.hail_size} and is {warning.hail_threat}")

                elif i == 4:
                    if warning.tornado_detection == None:
                        continue
                    else:
                        message_content.append(f"{line} {warning.tornado_detection}")

        message_content.append(storm_info[-1])
        content_string = '\n'.join(message_content)

        if "tornado" in warning.event_type.lower():
            embed_colour = discord.Colour.red()

        elif "thunderstorm" in warning.event_type.lower():
            embed_colour = discord.Colour.yellow()

        elif "flood" in warning.event_type.lower():
            embed_colour = discord.Colour.green()

        else:
            print(f"Unsupported Warning Type: {warning.event_type}")
            embed_colour = discord.Color.dark_grey()

        return discord.Embed(colour=embed_colour, title=warning.headline, description=content_string)

if __name__ == "__main__":
    print("This is a lib file")