import WarningManager
import Nyon_Util

import os
from dotenv import load_dotenv
from datetime import datetime, timezone

import discord
from discord.ext import tasks

NWS_API = "https://api.weather.gov/alerts/active"
CHANNEL_ASSOCIATIONS = {"nws-tornado": "tornado", "nws-severe-storm": "severe thunderstorm", "nws-special-weather": "special weather", "nws-flash-flood": "flash flood"} 

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

wm = WarningManager.WarningManager(NWS_API)

client = discord.Client(intents=discord.Intents.default())

@tasks.loop(minutes=1)
async def main_loop(thunderstorm_channel: discord.TextChannel, tornado_channel: discord.TextChannel, flood_channel: discord.TextChannel):

    warning_counts = {}
    sent_warnings = set()
    
    wm.update()

    if len(wm.warning_set) < 1:
        print(f"No warnings present")
        return

    print(f"Warnings Updated")
    print(f"Total Warnings: {len(wm.warning_set)}")

    await thunderstorm_channel.purge()
    await tornado_channel.purge()
    await flood_channel.purge()

    for warning in wm.warning_set:

        storm_info = [
            f"**Areas Listed:** {warning.area_desc}",
            f"**Description:** ```{warning.description}```",
            f"**Wind Gusts and Source:** {warning.wind_gust} / {warning.wind_threat}",
            f"**Hail Size and Source:** {warning.hail_size} / {warning.hail_threat},",
            f"**Tornado Threat:** {warning.tornado_detection}",
            f"Expires <t:{int(warning.expiration_time.timestamp())}:R>",
            f"-" * 40
        ]

        if warning.id not in sent_warnings:

            sent_warnings.add(warning.id)

            if "tornado" in warning.event_type.lower():
                warning_embed = discord.Embed(color=discord.Color.red(), title=warning.headline, description="\n".join(storm_info))
                await tornado_channel.send(embed=warning_embed, delete_after=(warning.expiration_time - datetime.now(timezone.utc)).total_seconds())
            if "thunderstorm" in warning.event_type.lower():
                warning_embed = discord.Embed(color=discord.Color.yellow(), title=warning.headline, description="\n".join(storm_info))
                await thunderstorm_channel.send(embed=warning_embed, delete_after=(warning.expiration_time - datetime.now(timezone.utc)).total_seconds())
            if "flood" in warning.event_type.lower():
                warning_embed = discord.Embed(color=discord.Color.green(), title=warning.headline, description="\n".join(storm_info))
                await flood_channel.send(embed=warning_embed, delete_after=(warning.expiration_time - datetime.now(timezone.utc)).total_seconds())

        try:
            warning_counts[warning.event_type] += 1
        except KeyError:
            warning_counts[warning.event_type] = 1
    
    for k, v in warning_counts.items():
        print(f"{k}:{v}")
    print("\n")

@client.event
async def on_ready():

    print(f"Bot loaded in as {client.user}")
    await client.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="Sniffing for warnings"))

    thunderstorm_channel: discord.TextChannel
    tornado_channel: discord.TextChannel
    flood_channel: discord.TextChannel

    for channel in client.get_all_channels():
        if channel.type == discord.ChannelType.text:
            if channel.name == "autobrad-thunderstorm":
                thunderstorm_channel = channel

    for channel in client.get_all_channels():
        if channel.type == discord.ChannelType.text:
            if channel.name == "autobrad-tornado":
                tornado_channel = channel

    for channel in client.get_all_channels():
        if channel.type == discord.ChannelType.text:
            if channel.name == "autobrad-flood":
                flood_channel = channel

    await thunderstorm_channel.purge()
    await tornado_channel.purge()
    await flood_channel.purge()

    main_loop.start(thunderstorm_channel, tornado_channel, flood_channel)

client.run(TOKEN)