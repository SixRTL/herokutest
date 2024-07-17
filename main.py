import os
import discord
from discord.ext import commands
import pymongo
import asyncio

# Initialize bot and set command prefix
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# MongoDB connection URI with database name specified
mongodb_uri = os.getenv('MONGODB_URI')

# Create a MongoDB client and connect to the database
try:
    client = pymongo.MongoClient(mongodb_uri)
    db = client.get_database('discord_bot')  # Connect to 'discord_bot' database
    collection = db['characters']  # Collection name for characters
    
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except pymongo.errors.ConnectionFailure:
    print("Failed to connect to MongoDB. Check your connection URI or MongoDB deployment.")
    exit()

# Dictionary mapping Pokémon natures to D&D stats
pokemon_nature_stats = {
    "Adamant": {"name": "Physical Prowess & Strength", "modifier": {"ATK": 2, "DEF": -1}},
    "Bashful": {"name": "Charisma & Speechcraft", "modifier": {}},
    "Bold": {"name": "Foraging & Perception", "modifier": {"DEF": 2, "ATK": -1}},
    "Brave": {"name": "Physical Prowess & Strength", "modifier": {"ATK": 2, "SPE": -1}},
    "Calm": {"name": "Charisma & Speechcraft", "modifier": {"Sp_DEF": 2, "ATK": -1}},
    "Careful": {"name": "Charisma & Speechcraft", "modifier": {"Sp_DEF": 2, "Sp_ATK": -1}},
    "Docile": {"name": "Intelligence & Knowledge", "modifier": {}},
    "Gentle": {"name": "Charisma & Speechcraft", "modifier": {"Sp_DEF": 2, "DEF": -1}},
    "Hardy": {"name": "Foraging & Perception", "modifier": {}},
    "Hasty": {"name": "Acrobatics & Stealth", "modifier": {"SPE": 2, "DEF": -1}},
    "Impish": {"name": "Acrobatics & Stealth", "modifier": {"DEF": 2, "Sp_ATK": -1}},
    "Jolly": {"name": "Acrobatics & Stealth", "modifier": {"SPE": 2, "Sp_ATK": -1}},
    "Lax": {"name": "Foraging & Perception", "modifier": {"DEF": 2, "Sp_DEF": -1}},
    "Lonely": {"name": "Physical Prowess & Strength", "modifier": {"ATK": 2, "DEF": -1}},
    "Mild": {"name": "Intelligence & Knowledge", "modifier": {"Sp_ATK": 2, "DEF": -1}},
    "Modest": {"name": "Intelligence & Knowledge", "modifier": {"Sp_ATK": 2, "ATK": -1}},
    "Naive": {"name": "Charisma & Speechcraft", "modifier": {"SPE": 2, "Sp_DEF": -1}},
    "Naughty": {"name": "Physical Prowess & Strength", "modifier": {"ATK": 2, "Sp_DEF": -1}},
    "Quiet": {"name": "Charisma & Speechcraft", "modifier": {"Sp_ATK": 2, "SPE": -1}},
    "Quirky": {"name": "Charisma & Speechcraft", "modifier": {}},
    "Rash": {"name": "Foraging & Perception", "modifier": {"Sp_ATK": 2, "Sp_DEF": -1}},
    "Relaxed": {"name": "Acrobatics & Stealth", "modifier": {"DEF": 2, "SPE": -1}},
    "Sassy": {"name": "Charisma & Speechcraft", "modifier": {"Sp_DEF": 2, "SPE": -1}},
    "Serious": {"name": "Intelligence & Knowledge", "modifier": {}},
    "Timid": {"name": "Acrobatics & Stealth", "modifier": {"SPE": 2, "ATK": -1}}
}

# Emoji reactions for stat choices
emoji_mapping = {
    'ATK': '⚔️',   # Sword for Attack
    'Sp_ATK': '🔮',  # Crystal ball for Special Attack
    'DEF': '🛡️',   # Shield for Defense
    'Sp_DEF': '🔒',  # Locked for Special Defense
    'SPE': '⚡'     # Lightning bolt for Speed
}

# Command to register a character with reaction-based stat distribution
@bot.command(name='register', help='Register your D&D character with a Pokémon nature and distribute 5 stat points.')
async def register_character(ctx, name: str, profession: str, nature: str):
    user_id = str(ctx.author.id)  # Convert user_id to string for MongoDB storage

    # Check if the character already exists for the user
    existing_character = collection.find_one({'user_id': user_id})
    if existing_character:
        await ctx.send('You have already registered a character.')
        return

    # Check if the provided nature is valid
    if nature.capitalize() not in pokemon_nature_stats:
        await ctx.send(f'Invalid nature. Please choose one of the following: {", ".join(pokemon_nature_stats.keys())}.')
        return

    # Remaining code for registering character...
    # (This part remains unchanged as it handles Discord interactions)

# Other commands remain the same, but make sure to replace tokens/URIs similarly.

# Command to view all available commands and their descriptions
@bot.command(name='help_menu', help='Display a menu of all available commands and their descriptions.')
async def help_menu(ctx):
    help_embed = discord.Embed(
        title='Command Menu',
        description='Use these commands to interact with the bot:',
        color=discord.Color.blurple()
    )

    # Add command descriptions here
    help_embed.add_field(name='!register <name> <profession> <nature>',
                         value='Register your character with a Pokémon nature and distribute 5 stat points.',
                         inline=False)
    help_embed.add_field(name='!distribute_stats',
                         value='Distribute additional stat points to your registered character using reactions.',
                         inline=False)
    help_embed.add_field(name='!level_up',
                         value='Manually level up your character and gain a stat point to distribute.',
                         inline=False)
    help_embed.add_field(name='!view_character',
                         value='View details of your registered character.',
                         inline=False)
    help_embed.add_field(name='!help_menu',
                         value='Display a menu of all available commands and their descriptions.',
                         inline=False)

    await ctx.send(embed=help_embed)

# Command to view character details with exact Pokémon nature and modifiers
@bot.command(name='view_character', help='View details of your registered character.')
async def view_character(ctx):
    user_id = str(ctx.author.id)  # Convert user_id to string for MongoDB storage

    # Find the character for the user
    character = collection.find_one({'user_id': user_id})
    if not character:
        await ctx.send('You have not registered a character yet.')
        return

    nature = character['nature']

    # Ensure the nature is a valid key in pokemon_nature_stats
    if nature not in pokemon_nature_stats:
        await ctx.send(f"Invalid nature '{nature}'. Please check your character's nature.")
        return

    nature_details = pokemon_nature_stats[nature]
    nature_name = nature
    nature_modifiers = nature_details.get('modifier', {})

    # Prepare modifiers text in one line
    modifiers_text = ', '.join([f'{stat}: +{value}' if value > 0 else f'{stat}: {value}' for stat, value in nature_modifiers.items()])

    embed = discord.Embed(
        title=f'{character["name"]} - {character["profession"]}',
        description=f'**Nature:** {nature_name}\n\n**Modifiers:** {modifiers_text}\n\n**Stats:**',
        color=discord.Color.green()
    )

    # Add all stats to the embed
    embed.add_field(name='ATK', value=character['ATK'], inline=True)
    embed.add_field(name='Sp_ATK', value=character['Sp_ATK'], inline=True)
    embed.add_field(name='DEF', value=character['DEF'], inline=True)
    embed.add_field(name='Sp_DEF', value=character['Sp_DEF'], inline=True)
    embed.add_field(name='SPE', value=character['SPE'], inline=True)

    await ctx.send(embed=embed)

# Command to manually level up the character and gain a stat point
@bot.command(name='level_up', help='Manually level up your character and gain a stat point to distribute.')
async def level_up(ctx):
    user_id = str(ctx.author.id)  # Convert user_id to string for MongoDB storage

    # Find the character for the user
    character = collection.find_one({'user_id': user_id})
    if not character:
        await ctx.send('You have not registered a character yet.')
        return

    # Check if character is max level (for illustration purposes, you can customize this logic)
    if character['level'] >= 100:
        await ctx.send('Your character is already at maximum level.')
        return

    # Increment the level and distribute an additional stat point
    collection.update_one(
        {'user_id': user_id},
        {'$inc': {'level': 1, 'stat_points': 1}}
    )
    await ctx.send('Congratulations! Your character has leveled up and gained 1 additional stat point.')

# Run the bot with the specified token from environment variable
bot_token = os.getenv('DISCORD_TOKEN')
bot.run(bot_token)
