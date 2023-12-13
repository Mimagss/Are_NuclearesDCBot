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

#                                                        ---Auto-Request---

    async def changeAutoRequestMode(self):
        self.autoRequest = not self.autoRequest

    async def auto_requester(self, ctx, settings):
        msg = await ctx.send(embed= await self.getEmbedMSG_TabletView(settings))
        while self.autoRequest:
            await asyncio.sleep(self.requestTime)
            ic()
            await msg.edit(embed= await self.getEmbedMSG_TabletView(settings))

#                                                        ---Embed-Messages---

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
        
#                                                        ---Getter---

    async def get_CORE_TEMP(self):
        """Gibt die Kerntemperatur zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP"}).text

    async def get_CORE_TEMP_OPERATIVE(self):
        """Gibt die Operative Kerntemperatur zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP_OPERATIVE"}).text 

    async def get_CORE_TEMP_MAX(self):
        """Gibt die Maximale Kerntemperatur zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP_MAX"}).text
    
    async def get_CORE_TEMP_MIN(self):
        """Gibt die Minimale Kerntemperatur zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP_MIN"}).text
    
    async def get_CORE_TEMP_RESIDUAL(self):
        """Gibt die restliche Kerntemperatur zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_TEMP_RESIDUAL"}).text

    async def get_CORE_PRESSURE(self):
        """Gibt den Kerndruck zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_PRESSURE"}).text

    async def get_CORE_PRESSURE_MAX(self):
        """Gibt den maximalen Kerndruck zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_PRESSURE_MAX"}).text
    
    async def get_CORE_PRESSURE_OPERATIVE(self):
        """Gibt den operativen Kerndruck zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_PRESSURE_OPERATIVE"}).text
    
    async def get_CORE_INTEGRITY(self):
        """Gibt den operativen Kerndruck zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_INTEGRITY"}).text

    async def get_CORE_INTEGRITY(self):
        """Gibt den operativen Kerndruck zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_INTEGRITY"}).text

    async def get_CORE_WEAR(self):
        """Gibt den Kernverschleiß zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_WEAR"}).text

    async def get_CORE_STATE(self):
        """Gibt den Kernstatus zurück"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_STATE"}).text
    
    async def get_CORE_STATE_CRITICALITY(self): # listener?
        """Gibt den Kernstatus zurück: ob er Kritisch ist"""
        return requests.get(settings.get('url'), params= {"Variable": "CORE_STATE_CRITICALITY"}).text
    
    async def get_CORE_CRITICAL_MASS_REACHED(self): # listener ?
        return requests.get(settings.get('url'), params= {"Variable": "CORE_CRITICAL_MASS_REACHED"}).text
    
    async def get_CORE_CRITICAL_MASS_REACHED_COUNTER(self): # listener ?
        return requests.get(settings.get('url'), params= {"Variable": "CORE_CRITICAL_MASS_REACHED_COUNTER"}).text
    
    async def get_CORE_IMMINENT_FUSION(self):
        return requests.get(settings.get('url'), params= {"Variable": "CORE_IMMINENT_FUSION"}).text

    async def get_CORE_READY_FOR_START(self): # listener
        return requests.get(settings.get('url'), params= {"Variable": "CORE_READY_FOR_START"}).text
    
    async def get_CORE_STEAM_PRESENT(self):
        return requests.get(settings.get('url'), params= {"Variable": "CORE_STEAM_PRESENT"}).text
    
    async def get_CORE_HIGH_STEAM_PRESENT(self):
        return requests.get(settings.get('url'), params= {"Variable": "CORE_HIGH_STEAM_PRESENT"}).text

    async def get_TIME(self):
        return requests.get(settings.get('url'), params= {"Variable": "TIME"}).text

    async def get_TIME_STAMP(self):
        return requests.get(settings.get('url'), params= {"Variable": "TIME_STAMP"}).text
    
    async def get_COOLANT_CORE_STATE(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_STATE"}).text

    async def get_COOLANT_CORE_PRESSURE(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_PRESSURE"}).text
    
    async def get_COOLANT_CORE_MAX_PRESSURE(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_MAX_PRESSURE"}).text

    async def get_COOLANT_CORE_VESSEL_TEMPERATURE(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_VESSEL_TEMPERATURE"}).text

    async def get_COOLANT_CORE_QUANTITY_IN_VESSEL(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_QUANTITY_IN_VESSEL"}).text
    
    async def get_COOLANT_CORE_PRIMARY_LOOP_LEVEL(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_PRIMARY_LOOP_LEVEL"}).text
    
    async def get_COOLANT_CORE_FLOW_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_FLOW_SPEED"}).text
    
    async def get_COOLANT_CORE_FLOW_ORDERED_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_FLOW_ORDERED_SPEED"}).text
    
    async def get_COOLANT_CORE_FLOW_REACHED_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_FLOW_REACHED_SPEED"}).text
    
    async def get_COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT"}).text
    
    async def get_COOLANT_CORE_QUANTITY_FREIGHT_PUMPS_PRESENT(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_QUANTITY_FREIGHT_PUMPS_PRESENT"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_0_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_0_STATUS"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_STATUS"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_STATUS"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_3_OVERLOAD_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_3_OVERLOAD_STATUS"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_0_ORDERED_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_0_ORDERED_SPEED"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_ORDERED_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_ORDERED_SPEED"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_ORDERED_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_ORDERED_SPEED"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_0_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_0_SPEED"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_1_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_1_SPEED"}).text
    
    async def get_COOLANT_CORE_CIRCULATION_PUMP_2_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "COOLANT_CORE_CIRCULATION_PUMP_2_SPEED"}).text
    
    async def get_RODS_STATUS(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_STATUS"}).text
    
    async def get_RODS_MOVEMENT_SPEED(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_MOVEMENT_SPEED"}).text
    
    async def get_RODS_MOVEMENT_SPEED_DECREASED_HIGH_TEMPERATURE(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_MOVEMENT_SPEED_DECREASED_HIGH_TEMPERATURE"}).text
    
    async def get_RODS_DEFORMED(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_DEFORMED"}).text
    
    async def get_RODS_TEMPERATURE(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_TEMPERATURE"}).text
    
    async def get_RODS_MAX_TEMPERATURE(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_MAX_TEMPERATURE"}).text
    
    async def get_RODS_POS_ORDERED(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_POS_ORDERED"}).text
    
    async def get_RODS_POS_ACTUAL(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_POS_ACTUAL"}).text
    
    async def get_RODS_POS_REACHED(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_POS_REACHED"}).text
    
    async def get_RODS_QUANTITY(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_QUANTITY"}).text
    
    async def get_RODS_ALIGNED(self):
        return requests.get(settings.get('url'), params= {"Variable": "RODS_ALIGNED"}).text

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

    @app_commands.command()
    async def start_auto_requester(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.auto_requester(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_temp(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_temp_operative(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_OPERATIVE(ctx= ctx, settings= self.settings))
    
    @app_commands.command()
    async def core_temp_max(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_MAX(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_temp_min(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_MIN(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_pressure(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_PRESSURE(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_pressure_max(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_PRESSURE_MAX(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_pressure_operative(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_PRESSURE_OPERATIVE(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_integrity(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_INTEGRITY(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_wear(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_WEAR(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_state(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_STATE(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_state_criticality(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_STATE_CRITICALITY(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_critical_mass_reached(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_CRITICAL_MASS_REACHED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_critical_mass_reached_counter(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_CRITICAL_MASS_REACHED_COUNTER(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_imminent_fusion(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_IMMINENT_FUSION(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_ready_for_start(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_READY_FOR_START(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_steam_present(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_STEAM_PRESENT(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_high_steam_present(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_HIGH_STEAM_PRESENT(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def time(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_TIME(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def time_stamp(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_TIME_STAMP(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_state(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_STATE(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_pressure(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_PRESSURE(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_max_pressure(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_MAX_PRESSURE(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_vessel_temperature(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_VESSEL_TEMPERATURE(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_quantity_in_vessel(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_QUANTITY_IN_VESSEL(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_primary_loop_level(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_PRIMARY_LOOP_LEVEL(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_flow_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_FLOW_SPEED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_flow_ordered_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_FLOW_ORDERED_SPEED(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def coolant_core_flow_reached_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_FLOW_REACHED_SPEED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_quantity_circulation_pumps_present(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_quantity_freight_pumps_present(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_QUANTITY_FREIGHT_PUMPS_PRESENT(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_0_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_STATUS(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_1_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_STATUS(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_2_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_STATUS(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_0_dry_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_1_dry_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def coolant_core_circulation_pump_2_dry_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_1_overload_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def coolant_core_circulation_pump_2_overload_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_3_overload_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_3_OVERLOAD_STATUS(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_0_ordered_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_ORDERED_SPEED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_1_ordered_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_ORDERED_SPEED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_2_ordered_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_ORDERED_SPEED(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def coolant_core_circulation_pump_0_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_SPEED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_1_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_SPEED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def coolant_core_circulation_pump_2_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_SPEED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def rods_status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_STATUS(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def rods_movement_speed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_MOVEMENT_SPEED(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def rods_movement_speed_decreased_high_temperature(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_MOVEMENT_SPEED_DECREASED_HIGH_TEMPERATURE(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def rods_deformed(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_DEFORMED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def rods_temperature(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_TEMPERATURE(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def rods_max_temperature(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_MAX_TEMPERATURE(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def rods_pos_ordered(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_POS_ORDERED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def rods_pos_actual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_POS_ACTUAL(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def rods_pos_reached(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_POS_REACHED(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def rods_quantity(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_QUANTITY(ctx= ctx, settings= self.settings))

    @app_commands.command()
    async def core_temp_residual(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))
        
    @app_commands.command()
    async def rods_aligned(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        await ctx.send(embed= await self.nucleARES.get_RODS_ALIGNED(ctx= ctx, settings= self.settings))
 
class NucleARES_Prefix_Commands(commands.Cog):
    def __init__(self, debug : bool, settings : dict) -> None:
        self.debug = debug
        self.settings = settings
        self.nucleARES : NucleARES = NucleARES(debug= debug, requestTime= settings.get('requestTime'))

    @commands.command()
    async def start_auto_requester(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.auto_requester(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_temp(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_temp_operative(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_OPERATIVE(ctx= ctx, settings= self.settings))
    
    @commands.command()
    async def core_temp_max(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_MAX(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_temp_min(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_MIN(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_pressure(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_PRESSURE(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_pressure_max(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_PRESSURE_MAX(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_pressure_operative(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_PRESSURE_OPERATIVE(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_integrity(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_INTEGRITY(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_wear(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_WEAR(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_state(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_STATE(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_state_criticality(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_STATE_CRITICALITY(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_critical_mass_reached(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_CRITICAL_MASS_REACHED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_critical_mass_reached_counter(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_CRITICAL_MASS_REACHED_COUNTER(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_imminent_fusion(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_IMMINENT_FUSION(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_ready_for_start(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_READY_FOR_START(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_steam_present(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_STEAM_PRESENT(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_high_steam_present(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_HIGH_STEAM_PRESENT(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def time(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_TIME(ctx= ctx, settings= self.settings))

    @commands.command()
    async def time_stamp(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_TIME_STAMP(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_state(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_STATE(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_pressure(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_PRESSURE(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_max_pressure(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_MAX_PRESSURE(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_vessel_temperature(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_VESSEL_TEMPERATURE(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_quantity_in_vessel(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_QUANTITY_IN_VESSEL(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_primary_loop_level(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_PRIMARY_LOOP_LEVEL(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_flow_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_FLOW_SPEED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_flow_ordered_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_FLOW_ORDERED_SPEED(ctx= ctx, settings= self.settings))

    @commands.command()
    async def coolant_core_flow_reached_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_FLOW_REACHED_SPEED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_quantity_circulation_pumps_present(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_QUANTITY_CIRCULATION_PUMPS_PRESENT(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_quantity_freight_pumps_present(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_QUANTITY_FREIGHT_PUMPS_PRESENT(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_0_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_STATUS(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_STATUS(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_2_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_STATUS(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_0_dry_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_DRY_STATUS(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_dry_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_DRY_STATUS(ctx= ctx, settings= self.settings))

    @commands.command()
    async def coolant_core_circulation_pump_2_dry_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_DRY_STATUS(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_overload_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_OVERLOAD_STATUS(ctx= ctx, settings= self.settings))

    @commands.command()
    async def coolant_core_circulation_pump_2_overload_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_OVERLOAD_STATUS(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_3_overload_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_3_OVERLOAD_STATUS(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_0_ordered_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_ORDERED_SPEED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_ordered_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_ORDERED_SPEED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_2_ordered_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_ORDERED_SPEED(ctx= ctx, settings= self.settings))

    @commands.command()
    async def coolant_core_circulation_pump_0_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_0_SPEED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_1_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_1_SPEED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def coolant_core_circulation_pump_2_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_COOLANT_CORE_CIRCULATION_PUMP_2_SPEED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def rods_status(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_STATUS(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def rods_movement_speed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_MOVEMENT_SPEED(ctx= ctx, settings= self.settings))

    @commands.command()
    async def rods_movement_speed_decreased_high_temperature(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_MOVEMENT_SPEED_DECREASED_HIGH_TEMPERATURE(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def rods_deformed(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_DEFORMED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def rods_temperature(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_TEMPERATURE(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def rods_max_temperature(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_MAX_TEMPERATURE(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))

    @commands.command()
    async def rods_pos_ordered(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_POS_ORDERED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def rods_pos_actual(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_POS_ACTUAL(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def rods_pos_reached(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_POS_REACHED(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def rods_quantity(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_QUANTITY(ctx= ctx, settings= self.settings))

    @commands.command()
    async def core_temp_residual(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_CORE_TEMP_RESIDUAL(ctx= ctx, settings= self.settings))
        
    @commands.command()
    async def rods_aligned(self, ctx) -> None:
        await ctx.send(embed= await self.nucleARES.get_RODS_ALIGNED(ctx= ctx, settings= self.settings))
        
if __name__ == "__main__":
    TOKEN = bot_settings.get('token')
    client.run(TOKEN)