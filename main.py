import discord
from discord.ext import commands
import pymongo
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file (only for local development)
load_dotenv()

# Initialize bot and set command prefix
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# MongoDB connection URI with database name specified
MONGODB_URI = os.getenv('MONGODB_URI')

# Check if the MongoDB URI is set
if MONGODB_URI is None:
    print('MONGODB_URI environment variable is not set. Please set it in your .env file.')
    exit()

# Create a MongoDB client and connect to the database
try:
    client = pymongo.MongoClient(MONGODB_URI)
    db = client.get_database('discord_bot')  # Connect to 'discord_bot' database
    collection = db['characters']  # Collection name for characters
    
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except pymongo.errors.ConnectionFailure:
    print("Failed to connect to MongoDB. Check your connection URI or MongoDB deployment.")
    exit()

# Discord bot token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Check if the Discord token is set
if DISCORD_TOKEN is None:
    print('DISCORD_TOKEN environment variable is not set. Please set it in your .env file.')
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

    # Initial stat distribution menu
    stat_distribution = {
        'ATK': 0,
        'Sp_ATK': 0,
        'DEF': 0,
        'Sp_DEF': 0,
        'SPE': 0
    }

    stat_points_left = 5

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in emoji_mapping.values()

    message = await ctx.send(f"React with emojis to distribute your stat points. You have {stat_points_left} points left.")

    for emoji in emoji_mapping.values():
        await message.add_reaction(emoji)

    while stat_points_left > 0:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            emoji_str = str(reaction.emoji)

            for stat, emoji in emoji_mapping.items():
                if emoji == emoji_str:
                    stat_choice = stat

            # Prompt user for points to allocate
            await ctx.send(f'How many points do you want to allocate to {stat_choice}? (Remaining points: {stat_points_left})')

            def points_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

            try:
                points_msg = await bot.wait_for('message', timeout=60.0, check=points_check)
                points = int(points_msg.content)

                if points > stat_points_left or points < 0:
                    await ctx.send(f'Invalid number of points. You can allocate between 0 and {stat_points_left} points.')
                    continue

                # Update stat distribution
                stat_distribution[stat_choice] += points
                stat_points_left -= points

                # Update reactions to show remaining points
                for emoji in emoji_mapping.values():
                    await message.clear_reaction(emoji)

                for stat, emoji in emoji_mapping.items():
                    await message.add_reaction(emoji)

                await message.edit(content=f"React with emojis to distribute your stat points. You have {stat_points_left} points left.")

            except asyncio.TimeoutError:
                await ctx.send('Stat allocation timed out. Please start again.')
                return

        except asyncio.TimeoutError:
            await ctx.send('Stat allocation timed out. Please start again.')
            return

    # Insert character into MongoDB with level 5 and stat distribution
    character_data = {
        'user_id': user_id,
        'name': name,
        'profession': profession,
        'level': 5,
        'nature': nature.capitalize(),
        'stat_points': 0,
        'ATK': stat_distribution['ATK'],
        'Sp_ATK': stat_distribution['Sp_ATK'],
        'DEF': stat_distribution['DEF'],
        'Sp_DEF': stat_distribution['Sp_DEF'],
        'SPE': stat_distribution['SPE']
    }

    collection.insert_one(character_data)
    await ctx.send(f'Character {name} registered successfully with profession {profession} and nature {nature.capitalize()}, associated with {pokemon_nature_stats[nature.capitalize()]["name"]}.')

# Command to distribute additional stat points using reactions
@bot.command(name='distribute_stats', help='Distribute additional stat points to your registered character using reactions.')
async def distribute_stats(ctx):
    user_id = str(ctx.author.id)  # Convert user_id to string for MongoDB storage

    # Check if the user has registered a character
    existing_character = collection.find_one({'user_id': user_id})
    if not existing_character:
        await ctx.send('You have not registered a character yet. Use !register command to register one.')
        return

    stat_points_left = existing_character['stat_points']

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in emoji_mapping.values()

    message = await ctx.send(f"React with emojis to distribute your {stat_points_left} additional stat points.")

    for emoji in emoji_mapping.values():
        await message.add_reaction(emoji)

    while stat_points_left > 0:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            emoji_str = str(reaction.emoji)

            for stat, emoji in emoji_mapping.items():
                if emoji == emoji_str:
                    stat_choice = stat

            # Prompt user for points to allocate
            await ctx.send(f'How many points do you want to allocate to {stat_choice}? (Remaining points: {stat_points_left})')

            def points_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

            try:
                points_msg = await bot.wait_for('message', timeout=60.0, check=points_check)
                points = int(points_msg.content)

                if points > stat_points_left or points < 0:
                    await ctx.send(f'Invalid number of points. You can allocate between 0 and {stat_points_left} points.')
                    continue

                # Update character in MongoDB with additional stat points
                collection.update_one({'user_id': user_id}, {'$inc': {stat_choice: points, 'stat_points': -points}})
                stat_points_left -= points

                # Update reactions to show remaining points
                for emoji in emoji_mapping.values():
                    await message.clear_reaction(emoji)

                for stat, emoji in emoji_mapping.items():
                    await message.add_reaction(emoji)

                await message.edit(content=f"React with emojis to distribute your {stat_points_left} additional stat points.")

            except asyncio.TimeoutError:
                await ctx.send('Stat allocation timed out. Please start again.')
                return

        except asyncio.TimeoutError:
            await ctx.send('Stat allocation timed out. Please start again.')
            return

    await ctx.send('All additional stat points distributed successfully.')

# Run the bot with the Discord token
bot.run(DISCORD_TOKEN)
