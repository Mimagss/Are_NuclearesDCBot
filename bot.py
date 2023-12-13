#viel hilft viel
import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import asyncio
from icecream import ic
import requests

def getsettings() -> dict:
    """Gibt alle Settings zurück"""
    with open(f"{os.path.join(os.path.dirname(os.path.realpath(__file__)))}\\settings.json", 'r') as file:
        data = file.read()
        data = json.loads(data)
        file.close()
    return data

settings : dict = getsettings()
bot_settings : dict = settings.get('settings_bot')
intents = discord.Intents.all()
prefix = bot_settings.get('prefix')
client = commands.Bot(command_prefix=prefix ,intents= intents)
OWNER_ID : int = bot_settings.get('ownerId')

#                                                        ---Events---

@client.event
async def on_ready():#funktioniert
    # init Bot
    debugMode = True # Logs every Variable in commands on shell
    await client.add_cog(NucleARES_Slash_Commands(debug= debugMode, settings= settings.get('settings_NucleARES')))
    await client.add_cog(NucleARES_Prefix_Commands(debug= debugMode, settings= settings.get('settings_NucleARES')))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"Mit sich selbst"))
    ic("Online")
    await client.tree.sync()
    user = client.get_user(OWNER_ID)
    await user.send("Klar soweit!")

class NucleARES(commands.Cog):
    def __init__(self, debug : bool, requestTime) -> None:
        self.debug = debug # feature
        self.autoRequest = True
        self.requestTime : int = requestTime#10#360
        #requests.get(settings.get('url'), params= {"Variable": "RODS_ALIGNED"})
#                                                        ---Core---
    async def changeAutoRequestMode(self):
        self.autoRequest = not self.autoRequest

    async def auto_requester(self, ctx, settings):
        msg = await ctx.send(embed= await self.getEmbedMSG_TabletView(settings))
        while self.autoRequest:
            await asyncio.sleep(self.requestTime)
            ic()
            await msg.edit(embed= await self.getEmbedMSG_TabletView(settings))

    async def getEmbedMSG_TabletView(self, settings : dict):
        embed = discord.Embed(
            title= "Tablet View"
        )
        # embed.add_field(name="", value="", inline= False)
        embed.add_field(name="Ingame Zeit", value= f"{requests.get(settings.get('url'), params= {"Variable": "TIME"}).text}", inline= False)
        embed.add_field(name="Core", value= f"{requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP"}).text} C° | {requests.get(settings.get('url'), params= {"Variable": "CORE_PRESSURE"}).text} BAR", inline= False)
        embed.add_field(name="Pressurizer", value="no api info", inline= False) #f"{requests.get(settings.get('url'), params= {"Variable": "CORE_INTEGRITY"}).text} %", inline= False)
        embed.add_field(name="Steam Generator", value="no api info", inline= False) #value=f"{requests.get(settings.get('url'), params= {"Variable": "CORE_STATE"}).text}", inline= False)
        
        #keine ahnung welche der API befehle da richtig ist, hab einfach einen genommen der da war
        embed.add_field(name="Core Circulation Pump 1", value=f"{requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_0_SPEED"}).text}", inline= False)
        embed.add_field(name="Core Circulation Pump 2", value=f"{requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_SPEED"}).text}", inline= False)
        embed.add_field(name="Core Circulation Pump 3", value=f"{requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_SPEED"}).text}", inline= False)
        
        embed.add_field(name="Generator Turbine", value="no api info", inline= False)# value=f"{requests.get(settings.get('url'), params= {"Variable": "CORE_READY_FOR_START"}).text}", inline= False)
        embed.add_field(name="Condenser", value="no api info", inline= False)# value= requests.get(settings.get('url'), params= {"Variable": "RODS_ALIGNED"}).text, inline= False)
        embed.add_field(name="Condenser Circulation Pump", value="no api info", inline= False)# value= requests.get(settings.get('url'), params= {"Variable": "RODS_ALIGNED"}).text, inline= False)
        embed.add_field(name="Condenser Cooling Pump", value="no api info", inline= False)# value= requests.get(settings.get('url'), params= {"Variable": "RODS_ALIGNED"}).text, inline= False)
        embed.add_field(name="Electric Turbine", value="no api info", inline= False)# value= requests.get(settings.get('url'), params= {"Variable": "RODS_ALIGNED"}).text, inline= False)
        return embed

    async def getEmbedMSG(self, settings : dict):
        embed = discord.Embed(
            title= "Core Status"
        )
        # embed.add_field(name="", value="", inline= False)
        embed.add_field(name="Ingame Zeit", value= f"{requests.get(settings.get('url'), params= {"Variable": "TIME"}).text}", inline= False)
        embed.add_field(name="Temperatur", value= f"{requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP"}).text} C°", inline= False)
        embed.add_field(name="Kern Intigrität", value=f"{requests.get(settings.get('url'), params= {"Variable": "CORE_INTEGRITY"}).text} %", inline= False)
        embed.add_field(name="Kernstatus", value=f"{requests.get(settings.get('url'), params= {"Variable": "CORE_STATE"}).text}", inline= False)
        embed.add_field(name="CORE_IMMINENT_FUSION", value=f"{requests.get(settings.get('url'), params= {"Variable": "CORE_IMMINENT_FUSION"}).text}", inline= False)
        embed.add_field(name="CORE_READY_FOR_START", value=f"{requests.get(settings.get('url'), params= {"Variable": "CORE_READY_FOR_START"}).text}", inline= False)
        embed.add_field(name="RODS_ALIGNED", value= requests.get(settings.get('url'), params= {"Variable": "RODS_ALIGNED"}).text, inline= False)
        return embed
    
class NucleARES_Slash_Commands(commands.Cog):
    def __init__(self, debug : bool, settings : dict) -> None:
        self.debug = debug
        self.settings = settings
        self.nucleARES : NucleARES = NucleARES(debug= debug, requestTime= settings.get('requestTime'))

    @app_commands.command()
    async def start_auto_requester(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.auto_requester(ctx= ctx, settings= self.settings))

class NucleARES_Prefix_Commands(commands.Cog):
    def __init__(self, debug : bool, settings : dict) -> None:
        self.debug = debug
        self.settings = settings
        self.nucleARES : NucleARES = NucleARES(debug= debug, requestTime= settings.get('requestTime'))

    @commands.command()
    async def start_auto_requester(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.auto_requester(ctx= ctx, settings= self.settings))

if __name__ == "__main__":
    TOKEN = bot_settings.get('token')
    client.run(TOKEN)