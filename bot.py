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
    await client.add_cog(NucleARES_Slash_Commands(debug= debugMode ,settings= settings.get('settings_NucleARES')))
    await client.add_cog(NucleARES_Prefix_Commands(debug= debugMode ,settings= settings.get('settings_NucleARES')))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"NucleARES"))
    ic("Online")
    await client.tree.sync()
    user = client.get_user(OWNER_ID)
    await user.send("Klar soweit!")

class NucleARES(commands.Cog):
    def __init__(self, debug : bool, autoRequest : bool, requestTime : int) -> None:
        self.debug : bool = debug # feature
        self.autoRequest : bool = autoRequest
        self.requestTime : int = requestTime
        ic.configureOutput(prefix= "LOG: ", outputFunction= self.log, includeContext= True)

#                                                        ---Logger---

    def getLogs(self):
        #open file in read modew
        with open(f"{os.path.dirname(__file__)}\\log.json", 'r') as file:
            #reads the file
            data = file.read()
            data = json.loads(data)
            file.close()
        return data

    def log(self, arg : str) -> None:
        """Logs the arg into the json file: log.json"""
        logs : dict[list] = self.getLogs()
        with open(f"{os.path.dirname(__file__)}/log.json", "w") as file:
            data = logs.get('logs').insert(0, arg)
            json.dump(data, file, sort_keys= True, indent= 4)
            file.close

#                                                        ---Listener and setter for the listener---

    async def changeAutoRequestMode(self, ctx, settings):
        self.autoRequest = not self.autoRequest
        if self.autoRequest:
            if self.requesting:
                return "Auto Request Enabled"
            await self.auto_requester(ctx, settings= settings)    
            return "Auto Request Enabled"
        else: 
            return "Auto Request Disabeld"

    async def auto_requester(self, ctx, settings):
        msg = await ctx.send(embed= await self.getEmbedMSG_TabletView(settings))
        while self.autoRequest:
            await asyncio.sleep(self.requestTime)
            await msg.edit(embed= await self.getEmbedMSG_TabletView(settings))

#                                                        ---Embed-Messages---

    async def getEmbedMSG_TabletView(self, settings : dict):
        embed = discord.Embed(
            title= "Tablet View"
        )
        # embed.add_field(name="", value="", inline= False)
        embed.add_field(name="Ingame Zeit", value= self.get_TIME(settings= settings), inline= False)
        embed.add_field(name="Core", value= f"{self.get_CORE_TEMP(settings= settings)} C° | {self.get_CORE_PRESSURE(settings= settings)} BAR", inline= False)
        embed.add_field(name="Pressurizer", value="no api info", inline= False) #value= f"{self.get_CORE_INTEGRITY(settings= settings)} %", inline= False)
        embed.add_field(name="Steam Generator", value="no api info", inline= False) #value= f"{self.get_CORE_STATE(settings= settings)}", inline= False)
        
        #keine ahnung welche der API befehle da richtig ist, hab einfach einen genommen der da war
        embed.add_field(name="Core Circulation Pump 1", value= self.get_COOLANT_CORE_CIRCULATION_PUMP_0_SPEED(settings= settings), inline= False)
        embed.add_field(name="Core Circulation Pump 2", value= self.get_COOLANT_CORE_CIRCULATION_PUMP_1_SPEED(settings= settings), inline= False)
        embed.add_field(name="Core Circulation Pump 3", value= self.get_COOLANT_CORE_CIRCULATION_PUMP_2_SPEED(settings= settings), inline= False)
        
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
        
#                                                        ---Getter---

    async def get_CORE_TEMP(self, settings : dict):
        """Gibt die Kerntemperatur zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP"}).text
        ic(result)
        return result
    
    async def get_CORE_TEMP_OPERATIVE(self, settings : dict):
        """Gibt die Operative Kerntemperatur zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP_OPERATIVE"}).text 
        ic(result)
        return result
    
    async def get_CORE_TEMP_MAX(self, settings : dict):
        """Gibt die Maximale Kerntemperatur zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP_MAX"}).text
        ic(result)
        return result
    
    async def get_CORE_TEMP_MIN(self, settings : dict):
        """Gibt die Minimale Kerntemperatur zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP_MIN"}).text
        ic(result)
        return result
    
    async def get_CORE_TEMP_RESIDUAL(self, settings : dict):
        """Gibt die restliche Kerntemperatur zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP_RESIDUAL"}).text
        ic(result)
        return result
    
    async def get_CORE_PRESSURE(self, settings : dict):
        """Gibt den Kerndruck zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_PRESSURE"}).text
        ic(result)
        return result
    
    async def get_CORE_PRESSURE_MAX(self, settings : dict):
        """Gibt den maximalen Kerndruck zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_PRESSURE_MAX"}).text
        ic(result)
        return result

    async def get_CORE_PRESSURE_OPERATIVE(self, settings : dict):
        """Gibt den operativen Kerndruck zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_PRESSURE_OPERATIVE"}).text
        ic(result)
        return result
    
    async def get_CORE_INTEGRITY(self, settings : dict):
        """Gibt den operativen Kerndruck zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_INTEGRITY"}).text
        ic(result)
        return result
    
    async def get_CORE_INTEGRITY(self, settings : dict):
        """Gibt den operativen Kerndruck zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_INTEGRITY"}).text
        ic(result)
        return result
    
    async def get_CORE_WEAR(self, settings : dict):
        """Gibt den Kernverschleiß zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_WEAR"}).text
        ic(result)
        return result
    
    async def get_CORE_STATE(self, settings : dict):
        """Gibt den Kernstatus zurück"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_STATE"}).text
        ic(result)
        return result

    async def get_CORE_STATE_CRITICALITY(self, settings : dict): # listener?
        """Gibt den Kernstatus zurück: ob er Kritisch ist"""
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_STATE_CRITICALITY"}).text
        ic(result)
        return result

    async def get_CORE_CRITICAL_MASS_REACHED(self, settings : dict): # listener ?
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_CRITICAL_MASS_REACHED"}).text
        ic(result)
        return result
    
    async def get_CORE_CRITICAL_MASS_REACHED_COUNTER(self, settings : dict): # listener ?
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_CRITICAL_MASS_REACHED_COUNTER"}).text
        ic(result)
        return result
    
    async def get_CORE_IMMINENT_FUSION(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_IMMINENT_FUSION"}).text
        ic(result)
        return result
    
    async def get_CORE_READY_FOR_START(self, settings : dict): # listener
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_READY_FOR_START"}).text
        ic(result)
        return result
    
    async def get_CORE_STEAM_PRESENT(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_STEAM_PRESENT"}).text
        ic(result)
        return result
    
    async def get_CORE_HIGH_STEAM_PRESENT(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "CORE_HIGH_STEAM_PRESENT"}).text
        ic(result)
        return result
    
    async def get_TIME(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "TIME"}).text
        ic(result)
        return result
    
    async def get_TIME_STAMP(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "TIME_STAMP"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_STATE(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_STATE"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_PRESSURE(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_PRESSURE"}).text
        ic(result)
        return result

    async def get_COOLANT_CORE_MAX_PRESSURE(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_MAX_PRESSURE"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_VESSEL_TEMPERATURE(self, settings):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_VESSEL_TEMPERATURE"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_QUANTITY_IN_VESSEL(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_QUANTITY_IN_VESSEL"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_PRIMARY_LOOP_LEVEL(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_PRIMARY_LOOP_LEVEL"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_FLOW_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_FLOW_SPEED"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_FLOW_ORDERED_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_FLOW_ORDERED_SPEED"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_FLOW_REACHED_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_FLOW_REACHED_SPEED"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_QUANTITY_FREIGHT_PUMPS_PRESENT(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_QUANTITY_FREIGHT_PUMPS_PRESENT"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_0_STATUS(self, settings : dict):
        result : str = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_0_STATUS"}).text
        if result == "0":
            result : str = "0: Inactive"
        elif result == "1":
            result : str = "1: Active, no speed reached"
        elif result == "2":
            result : str = "2: Active, speed reached"
        elif result == "3":
            result : str = "3: Requires maintenance"
        elif result == "4":
            result : str = "4: Not installed"
        elif result == "5":
            result : str = "5: Insufficient energy"
        else:
            result = "sth went wrong: get_COOLANT_CORE_CIRCULATION_PUMP_2_STATUS"
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_STATUS(self, settings : dict):
        result : str = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_STATUS"}).text
        if result == "0":
            result : str = "0: Inactive"
        elif result == "1":
            result : str = "1: Active, no speed reached"
        elif result == "2":
            result : str = "2: Active, speed reached"
        elif result == "3":
            result : str = "3: Requires maintenance"
        elif result == "4":
            result : str = "4: Not installed"
        elif result == "5":
            result : str = "5: Insufficient energy"
        else:
            result = "sth went wrong: get_COOLANT_CORE_CIRCULATION_PUMP_2_STATUS"
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_STATUS(self, settings : dict):
        result : str = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_STATUS"}).text
        if result == "0":
            result : str = "0: Inactive"
        elif result == "1":
            result : str = "1: Active, no speed reached"
        elif result == "2":
            result : str = "2: Active, speed reached"
        elif result == "3":
            result : str = "3: Requires maintenance"
        elif result == "4":
            result : str = "4: Not installed"
        elif result == "5":
            result : str = "5: Insufficient energy"
        else:
            result = "sth went wrong: get_COOLANT_CORE_CIRCULATION_PUMP_2_STATUS"
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS(self, settings : dict):
        result : str = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS"}).text
        if result == "1":
            result : str = "1: Active without fluid"
        elif result == "4":
            result : str = "4: Inactive or active with fluid"
        else:
            result = "sth went wrong: get_COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS"
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS(self, settings : dict):
        result : str = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS"}).text
        if result == "1":
            result : str = "1: Active without fluid"
        elif result == "4":
            result : str = "4: Inactive or active with fluid"
        else:
            result = "sth went wrong: get_COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS"
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS(self, settings : dict):
        result : str = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS"}).text
        if result == "1":
            result : str = "1: Active without fluid"
        elif result == "4":
            result : str = "4: Inactive or active with fluid"
        else:
            result = "sth went wrong: get_COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS"
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS(self, settings : dict):
        result : str = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS"}).text
        if result == "1":
            result : str = "1: Active and overload"
        elif result == "4":
            result : str = "4: Inactive or active no overload"
        else:
            result = "sth went wrong: get_COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS"
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS(self, settings : dict):
        result : str = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS"}).text
        if result == "1":
            result : str = "1: Active and overload"
        elif result == "4":
            result : str = "4: Inactive or active no overload"
        else:
            result = "sth went wrong: COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS"
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_3_OVERLOAD_STATUS(self, settings : dict):
        result : str = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_3_OVERLOAD_STATUS"}).text
        if result == "1":
            result : str = "1: Active and overload"
        elif result == "4":
            result : str = "4: Inactive or active no overload"
        else:
            result = "sth went wrong: COOLANT_CORE_CIRCULATION_PUMP_3_OVERLOAD_STATUS"
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_0_ORDERED_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_0_ORDERED_SPEED"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_ORDERED_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_ORDERED_SPEED"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_ORDERED_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_ORDERED_SPEED"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_0_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_0_SPEED"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_SPEED"}).text
        ic(result)
        return result
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_SPEED"}).text
        ic(result)
        return result
    
    async def get_RODS_STATUS(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_STATUS"}).text
        ic(result)
        return result
    
    async def get_RODS_MOVEMENT_SPEED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_MOVEMENT_SPEED"}).text
        ic(result)
        return result
    
    async def get_RODS_MOVEMENT_SPEED_DECREASED_HIGH_TEMPERATURE(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_MOVEMENT_SPEED_DECREASED_HIGH_TEMPERATURE"}).text
        ic(result)
        return result
    
    async def get_RODS_DEFORMED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_DEFORMED"}).text
        ic(result)
        return result
    
    async def get_RODS_TEMPERATURE(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_TEMPERATURE"}).text
        ic(result)
        return result
    
    async def get_RODS_MAX_TEMPERATURE(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_MAX_TEMPERATURE"}).text
        ic(result)
        return result
    
    async def get_RODS_POS_ORDERED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_POS_ORDERED"}).text
        ic(result)
        return result
    
    async def get_RODS_POS_ACTUAL(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_POS_ACTUAL"}).text
        ic(result)
        return result
    
    async def get_RODS_POS_REACHED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_POS_REACHED"}).text
        ic(result)
        return result
    
    async def get_RODS_QUANTITY(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_QUANTITY"}).text
        ic(result)
        return result
    
    async def get_RODS_ALIGNED(self, settings : dict):
        result = requests.get(settings.get('url'), params= {"Variable": "RODS_ALIGNED"}).text
        ic(result)
        return result

class NucleARES_Slash_Commands(commands.Cog):
    def __init__(self, debug : bool, settings : dict) -> None:
        self.debug = debug
        self.settings = settings
        self.nucleARES : NucleARES = NucleARES(debug= debug, autoRequest= settings.get('requestTime'), requestTime= settings.get('requestTime'))
    
    @app_commands.command()
    async def change_auto_request_mode(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.changeAutoRequestMode(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def start_auto_requester(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(embed= await self.nucleARES.auto_requester(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_temp(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP(settings= self.settings))

    @app_commands.command()
    async def core_temp_operative(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_OPERATIVE(settings= self.settings))
    
    @app_commands.command()
    async def core_temp_max(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_MAX(settings= self.settings))

    @app_commands.command()
    async def core_temp_min(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_MIN(settings= self.settings))

    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))

    @app_commands.command()
    async def core_pressure(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_PRESSURE(settings= self.settings))

    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))
        
    @app_commands.command()
    async def core_pressure_max(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_PRESSURE_MAX(settings= self.settings))
        
    @app_commands.command()
    async def core_pressure_operative(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_PRESSURE_OPERATIVE(settings= self.settings))
        
    @app_commands.command()
    async def core_integrity(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_INTEGRITY(settings= self.settings))
        
    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))

    @app_commands.command()
    async def core_wear(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_WEAR(settings= self.settings))
        
    @app_commands.command()
    async def core_state(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_STATE(settings= self.settings))
        
    @app_commands.command()
    async def core_state_criticality(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_STATE_CRITICALITY(settings= self.settings))
        
    @app_commands.command()
    async def core_critical_mass_reached(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_CRITICAL_MASS_REACHED(settings= self.settings))
        
    @app_commands.command()
    async def core_crit_mass_reached_counter(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_CRITICAL_MASS_REACHED_COUNTER(settings= self.settings))

    @app_commands.command()
    async def core_imminent_fusion(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_IMMINENT_FUSION(settings= self.settings))
        
    @app_commands.command()
    async def core_ready_for_start(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_READY_FOR_START(settings= self.settings))
        
    @app_commands.command()
    async def core_steam_present(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_STEAM_PRESENT(settings= self.settings))
        
    @app_commands.command()
    async def core_high_steam_present(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_HIGH_STEAM_PRESENT(settings= self.settings))
        
    @app_commands.command()
    async def time(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_TIME(settings= self.settings))

    @app_commands.command()
    async def time_stamp(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_TIME_STAMP(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_state(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_STATE(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_pressure(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_PRESSURE(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_max_pressure(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_MAX_PRESSURE(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_vessel_temperature(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_VESSEL_TEMPERATURE(settings= self.settings))

    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_quantity_in_vessel(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_QUANTITY_IN_VESSEL(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_primary_loop_level(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_PRIMARY_LOOP_LEVEL(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_flow_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_FLOW_SPEED(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_flow_ordered_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_FLOW_ORDERED_SPEED(settings= self.settings))

    @app_commands.command()
    async def coolant_core_flow_reached_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_FLOW_REACHED_SPEED(settings= self.settings))
        
    @app_commands.command()
    async def cool_core_circ_pumps_present(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT(settings= self.settings))
        
    @app_commands.command()
    async def cool_core_freight_pumps_present(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_QUANTITY_FREIGHT_PUMPS_PRESENT(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circ_pump_0_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_STATUS(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circ_pump_1_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_STATUS(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circ_pump_2_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_STATUS(settings= self.settings))
        
    @app_commands.command()
    async def cool_core_circ_pump_0_dry_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS(settings= self.settings))
        
    @app_commands.command()
    async def cool_core_circ_pump_1_dry_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS(settings= self.settings))

    @app_commands.command()
    async def cool_core_circ_pump_2_dry_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS(settings= self.settings))
        
    @app_commands.command()
    async def cool_core_circ_pump_1_ol_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS(settings= self.settings))

    @app_commands.command()
    async def cool_core_circ_pump_2_ol_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS(settings= self.settings))
        
    @app_commands.command()
    async def cool_core_circ_pump_3_ol_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_3_OVERLOAD_STATUS(settings= self.settings))
        
    @app_commands.command()
    async def cool_core_circ_pump_0_ordered(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_ORDERED_SPEED(settings= self.settings))
        
    @app_commands.command()
    async def cool_core_circ_pump_1_ordered(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_ORDERED_SPEED(settings= self.settings))
        
    @app_commands.command()
    async def cool_core_circ_pump_2_ordered(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_ORDERED_SPEED(settings= self.settings))

    @app_commands.command()
    async def coolant_core_circ_pump_0_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_SPEED(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circ_pump_1_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_SPEED(settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circ_pump_2_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_SPEED(settings= self.settings))
        
    @app_commands.command()
    async def rods_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_STATUS(settings= self.settings))
        
    @app_commands.command()
    async def rods_movement_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_MOVEMENT_SPEED(settings= self.settings))

    @app_commands.command()
    async def rods_move_speed_dec_high_temp(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_MOVEMENT_SPEED_DECREASED_HIGH_TEMPERATURE(settings= self.settings))
        
    @app_commands.command()
    async def rods_deformed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_DEFORMED(settings= self.settings))
        
    @app_commands.command()
    async def rods_temperature(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_TEMPERATURE(settings= self.settings))
        
    @app_commands.command()
    async def rods_max_temperature(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_MAX_TEMPERATURE(settings= self.settings))
        
    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))

    @app_commands.command()
    async def rods_pos_ordered(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_POS_ORDERED(settings= self.settings))
        
    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))
        
    @app_commands.command()
    async def rods_pos_actual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_POS_ACTUAL(settings= self.settings))
        
    @app_commands.command()
    async def rods_pos_reached(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_POS_REACHED(settings= self.settings))
        
    @app_commands.command()
    async def rods_quantity(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_QUANTITY(settings= self.settings))

    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))
        
    @app_commands.command()
    async def rods_aligned(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_ALIGNED(settings= self.settings))
 
class NucleARES_Prefix_Commands(commands.Cog):
    def __init__(self, debug : bool, settings : dict) -> None:
        self.debug : bool = debug
        self.settings : dict  = settings
        self.nucleARES : NucleARES = NucleARES(debug= debug, autoRequest= settings.get('requestTime'), requestTime= settings.get('requestTime'))

    @commands.command()
    async def change_auto_request_mode(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.changeAutoRequestMode(ctx= ctx, settings= self.settings))

    @commands.command()
    async def start_auto_requester(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(embed= await self.nucleARES.auto_requester(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_temp(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP(settings= self.settings))

    @commands.command()
    async def core_temp_operative(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_OPERATIVE(settings= self.settings))
    
    @commands.command()
    async def core_temp_max(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_MAX(settings= self.settings))

    @commands.command()
    async def core_temp_min(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_MIN(settings= self.settings))

    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))

    @commands.command()
    async def core_pressure(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_PRESSURE(settings= self.settings))

    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))
        
    @commands.command()
    async def core_pressure_max(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_PRESSURE_MAX(settings= self.settings))
        
    @commands.command()
    async def core_pressure_operative(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_PRESSURE_OPERATIVE(settings= self.settings))
        
    @commands.command()
    async def core_integrity(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_INTEGRITY(settings= self.settings))
        
    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))

    @commands.command()
    async def core_wear(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_WEAR(settings= self.settings))
        
    @commands.command()
    async def core_state(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_STATE(settings= self.settings))
        
    @commands.command()
    async def core_state_criticality(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_STATE_CRITICALITY(settings= self.settings))
        
    @commands.command()
    async def core_critical_mass_reached(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_CRITICAL_MASS_REACHED(settings= self.settings))
        
    @commands.command()
    async def core_critical_mass_reached_counter(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_CRITICAL_MASS_REACHED_COUNTER(settings= self.settings))

    @commands.command()
    async def core_imminent_fusion(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_IMMINENT_FUSION(settings= self.settings))
        
    @commands.command()
    async def core_ready_for_start(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_READY_FOR_START(settings= self.settings))
        
    @commands.command()
    async def core_steam_present(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_STEAM_PRESENT(settings= self.settings))
        
    @commands.command()
    async def core_high_steam_present(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_HIGH_STEAM_PRESENT(settings= self.settings))
        
    @commands.command()
    async def time(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_TIME(settings= self.settings))

    @commands.command()
    async def time_stamp(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_TIME_STAMP(settings= self.settings))
        
    @commands.command()
    async def coolant_core_state(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_STATE(settings= self.settings))
        
    @commands.command()
    async def coolant_core_pressure(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_PRESSURE(settings= self.settings))
        
    @commands.command()
    async def coolant_core_max_pressure(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_MAX_PRESSURE(settings= self.settings))
        
    @commands.command()
    async def coolant_core_vessel_temperature(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_VESSEL_TEMPERATURE(settings= self.settings))

    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))
        
    @commands.command()
    async def coolant_core_quantity_in_vessel(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_QUANTITY_IN_VESSEL(settings= self.settings))
        
    @commands.command()
    async def coolant_core_primary_loop_level(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_PRIMARY_LOOP_LEVEL(settings= self.settings))
        
    @commands.command()
    async def coolant_core_flow_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_FLOW_SPEED(settings= self.settings))
        
    @commands.command()
    async def coolant_core_flow_ordered_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_FLOW_ORDERED_SPEED(settings= self.settings))

    @commands.command()
    async def coolant_core_flow_reached_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_FLOW_REACHED_SPEED(settings= self.settings))
        
    @commands.command()
    async def coolant_core_quantity_circulation_pumps_present(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT(settings= self.settings))
        
    @commands.command()
    async def coolant_core_quantity_freight_pumps_present(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_QUANTITY_FREIGHT_PUMPS_PRESENT(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_0_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_STATUS(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_STATUS(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_2_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_STATUS(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_0_dry_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_dry_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS(settings= self.settings))

    @commands.command()
    async def coolant_core_circulation_pump_2_dry_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_overload_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS(settings= self.settings))

    @commands.command()
    async def coolant_core_circulation_pump_2_overload_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_3_overload_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_3_OVERLOAD_STATUS(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_0_ordered_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_ORDERED_SPEED(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_ordered_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_ORDERED_SPEED(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_2_ordered_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_ORDERED_SPEED(settings= self.settings))

    @commands.command()
    async def coolant_core_circulation_pump_0_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_SPEED(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_SPEED(settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_2_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_SPEED(settings= self.settings))
        
    @commands.command()
    async def rods_status(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_STATUS(settings= self.settings))
        
    @commands.command()
    async def rods_movement_speed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_MOVEMENT_SPEED(settings= self.settings))

    @commands.command()
    async def rods_movement_speed_decreased_high_temperature(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_MOVEMENT_SPEED_DECREASED_HIGH_TEMPERATURE(settings= self.settings))
        
    @commands.command()
    async def rods_deformed(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_DEFORMED(settings= self.settings))
        
    @commands.command()
    async def rods_temperature(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_TEMPERATURE(settings= self.settings))
        
    @commands.command()
    async def rods_max_temperature(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_MAX_TEMPERATURE(settings= self.settings))
        
    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))

    @commands.command()
    async def rods_pos_ordered(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_POS_ORDERED(settings= self.settings))
        
    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))
        
    @commands.command()
    async def rods_pos_actual(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_POS_ACTUAL(settings= self.settings))
        
    @commands.command()
    async def rods_pos_reached(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_POS_REACHED(settings= self.settings))
        
    @commands.command()
    async def rods_quantity(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_QUANTITY(settings= self.settings))

    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_CORE_TEMP_RESIDUAL(settings= self.settings))
        
    @commands.command()
    async def rods_aligned(self, ctx) -> None:
        ic(ctx.message.author)
        await ctx.send(await self.nucleARES.get_RODS_ALIGNED(settings= self.settings))
        
if __name__ == "__main__":
    TOKEN = bot_settings.get('token')
    client.run(TOKEN)