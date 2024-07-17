import discord
from discord.ext import commands
import logging
import random
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Ensure the bot can manage members and roles
bot = commands.Bot(command_prefix='!', intents=intents)

# Set up logging
logging.basicConfig(level=logging.INFO)  # You can adjust the logging level here
logger = logging.getLogger()

# Define the quiz questions and answers
questions = [
    {"question": "Your favourite person's birthday is coming up. What do you get them?", "answers": ["A two-way ticket to a great vacation!", "A book of their favourite genre.", "A cute plushie.", "A cool new jacket!"]},
    {"question": "What is your ideal vacation?", "answers": ["A thrilling adventure!", "A peaceful retreat.", "A nature hike.", "A fun trip with friends!"]},
    {"question": "How do you prefer to solve problems?", "answers": ["By thinking things through.", "By exploring and figuring things out.", "By seeking advice from others.", "By taking action."]},
    {"question": "What do you consider to be your biggest fear?", "answers": ["I'm not afraid of anything!", "Remaining unfulfilled.", "The dark.", "Losing my friends and family."]},
    {"question": "Which of these activities sounds most fun?", "answers": ["Exploring the outdoors!", "Reading or watching TV.", "Going for a walk.", "Playing games with friends!"]},
    {"question": "Your friend makes a joke that kind of hurt your feelings. What do you do?", "answers": ["Laugh along with them! It's funny!", "Stay silent.", "Cry a little bit, but don't let them know.", "Be honest with them and say it hurt."]},
]

# Define Pokémon natures and recommended starter Pokémon based on answers
results = {
    "A two-way ticket to a great vacation!": {"nature": "Jolly", "pokemon": "Charmander", "description": "Jolly nature is energetic and loves adventure. Alternate suggestion: Bagon."},
    "Stay silent.": {"nature": "Lonely", "pokemon": "Turtwig", "description": "Lonely nature is soul with a kind heart. Alternate suggestion: Gible."},
    "Laugh along with them! It's funny!": {"nature": "Brave", "pokemon": "Charmander", "description": "Brave nature is a natural born leader. Alternate suggestion: Bagon."},
    "A book of their favourite genre.": {"nature": "Calm", "pokemon": "Bulbasaur", "description": "Calm nature enjoys relaxation and peace. Alternate suggestion: Dratini."},
    "A cute plushie.": {"nature": "Quiet", "pokemon": "Squirtle", "description": "Quiet nature prefers a peaceful and thoughtful environment. Alternate suggestion: Goomy"},
    "A cool new jacket!": {"nature": "Hasty", "pokemon": "Pikachu", "description": "Hasty nature is sociable and enjoys fun with friends. Alternate suggestion: Frigibax."},
    "A thrilling adventure!": {"nature": "Adamant", "pokemon": "Torchic", "description": "Adamant nature is bold and loves excitement. Alternate suggestion: Jangmo-o."},
    "A peaceful retreat.": {"nature": "Modest", "pokemon": "Chikorita", "description": "Modest nature values serenity and calm. Alternate suggestion: Dratini."},
    "A nature hike.": {"nature": "Gentle", "pokemon": "Treecko", "description": "Gentle nature appreciates nature and exploration. Alternate suggestion: Goomy."},
    "A fun trip with friends!": {"nature": "Bold", "pokemon": "Squirtle", "description": "Bold nature enjoys adventure and fun with others. Alternate suggestion: Jangmo-o."},
    "By thinking things through.": {"nature": "Sassy", "pokemon": "Totodile", "description": "Sassy nature prefers careful planning and thought. Alternate suggestion: Dreepy."},
    "By exploring and figuring things out.": {"nature": "Naive", "pokemon": "Mudkip", "description": "Naive nature loves exploration and discovery. Alternate suggestion: Beldum."},
    "By seeking advice from others.": {"nature": "Careful", "pokemon": "Piplup", "description": "Careful nature seeks wisdom and advice. Alternate suggestion: Beldum."},
    "By taking action.": {"nature": "Impish", "pokemon": "Turtwig", "description": "Impish nature is proactive and likes to take action. Alternate suggestion: Deino."},
    "I'm not afraid of anything!": {"nature": "Rash", "pokemon": "Charmander", "description": "Rash nature is bold and enthusiastic. Alternate suggestion: Deino."},
    "Remaining unfulfilled.": {"nature": "Relaxed", "pokemon": "Bulbasaur", "description": "Relaxed nature is calm and enjoys tranquility. Alternate suggestion: Dreepy."},
    "The dark.": {"nature": "Timid", "pokemon": "Cyndaquil", "description": "Timid nature is shy and prefers a quiet life. Alternate suggestion: Larvitar."},
    "Losing my friends and family.": {"nature": "Lax", "pokemon": "Pikachu", "description": "Lax nature is laid-back and cheerful. Alternate suggestion: Larvitar."},
    "Exploring the outdoors!": {"nature": "Naive", "pokemon": "Treecko", "description": "Naive nature loves adventure and outdoor activities. Alternate suggestion: Dratini."},
    "Reading or watching TV.": {"nature": "Quiet", "pokemon": "Piplup", "description": "Quiet nature enjoys calm and indoor activities. Alternate suggestion: Frigibax."},
    "Going for a walk.": {"nature": "Gentle", "pokemon": "Eevee", "description": "Gentle nature appreciates peaceful walks and nature. Alternate suggestion: Dratini."},
    "Playing games with friends!": {"nature": "Bold", "pokemon": "Riolu", "description": "Bold nature is fun-loving and enjoys games with friends. Alternate suggestion: Gible."},
}

# Dictionary to keep track of asked questions for each user
asked_questions = {}

# Command to start the quiz
@bot.command(name='invoke')
async def quiz(ctx):
    logger.info(f"Quiz command invoked by {ctx.author}")  # Log the command invocation
    user_answers = []

    # Initialize asked_questions for the user
    if ctx.author.id not in asked_questions:
        asked_questions[ctx.author.id] = set()

    # Shuffle the questions (optional)
    random.shuffle(questions)

    # Ask the questions
    for q in questions:
        # Check if the question has already been asked to this user
        if q["question"] in asked_questions[ctx.author.id]:
            continue
        
        question = q["question"]
        answers = q["answers"]
        answer_str = "\n".join([f"{i+1}. {a}" for i, a in enumerate(answers)])
        prompt = f"{question}\n{answer_str}"

        try:
            await ctx.author.send(prompt)
            logger.info(f"Sent question to {ctx.author}: {prompt}")  # Log the question sent

            def check(m):
                return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

            msg = await bot.wait_for('message', timeout=120.0, check=check)
            answer_index = int(msg.content) - 1
            if 0 <= answer_index < len(answers):
                user_answers.append(answers[answer_index])
                logger.info(f"{ctx.author} answered: {answers[answer_index]}")  # Log the answer received
            else:
                await ctx.author.send("Invalid choice. Please choose a valid option.")
                logger.warning(f"{ctx.author} provided invalid choice: {msg.content}")  # Log invalid choice
                return
        except asyncio.TimeoutError:
            await ctx.author.send("You took too long to respond.")
            logger.warning(f"{ctx.author} took too long to respond.")  # Log timeout
            return

        # Add the asked question to the user's set
        asked_questions[ctx.author.id].add(q["question"])

    # Determine the nature based on the most frequent answer
    if user_answers:
        most_common_answer = max(set(user_answers), key=user_answers.count)
        result = results.get(most_common_answer, {"nature": "Unknown", "pokemon": "Unknown", "description": "No suitable nature found."})
        nature = result["nature"]
        pokemon = result["pokemon"]
        description = result["description"]

        # Find the role based on the nature name
        role = discord.utils.get(ctx.guild.roles, name=nature)
        if role:
            try:
                await ctx.author.add_roles(role)
                logger.info(f"Assigned role {role.name} to {ctx.author}")  # Log the role assignment
            except discord.Forbidden:
                await ctx.author.send(f"I do not have permission to assign the role '{nature}'. Please make sure the role exists and is above my role in the role hierarchy.")
                logger.error(f"Permission error when assigning role '{nature}' to {ctx.author}")
            except discord.HTTPException as e:
                await ctx.author.send(f"An error occurred while assigning the role '{nature}'.")
                logger.error(f"HTTP Exception: {e}")
        else:
            await ctx.author.send(f"Role '{nature}' does not exist. Please create a role with this name.")
            logger.warning(f"Role '{nature}' does not exist for {ctx.author}")

        await ctx.author.send(f"Based on your answers, your Pokémon nature is **{nature}**.\nRecommended Starter Pokémon: **{pokemon}**\n{description}")
        logger.info(f"{ctx.author}'s Pokémon nature result: {nature}, Starter Pokémon: {pokemon}")  # Log the final result
    else:
        await ctx.author.send("No valid answers were received. Please try again.")
        logger.warning(f"No valid answers received from {ctx.author}")

    # Remove the user from asked_questions to reset for next session (optional)
    del asked_questions[ctx.author.id]

# Event when the bot is ready
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')  # Log the bot's login

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
