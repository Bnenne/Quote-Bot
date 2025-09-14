import discord
from discord.ext import commands
import aiohttp
import os

BOT_TOKEN = os.environ['BOT_TOKEN']

TOKEN = BOT_TOKEN
TARGET_CHANNEL_ID = 1391906913142444082  # replace with your channel ID

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class ChoiceButton(discord.ui.Button):
    def __init__(self, label, message, prediction, view):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.message = message
        self.prediction = prediction
        self.parent_view = view

    async def callback(self, interaction: discord.Interaction):
        # Only the original message author can click
        if interaction.user != self.message.author:
            await interaction.response.send_message(
                "Only the original message author can select!",
                ephemeral=True
            )
            return

        # Check prediction
        if self.label == self.prediction:
            response_text = "Yippee! I knew it."
        else:
            response_text = "Damnit..."

        # Disable all buttons
        for button in self.parent_view.children:
            button.disabled = True
        await interaction.message.edit(view=self.parent_view)

        await interaction.response.send_message(response_text)

class ChoiceView(discord.ui.View):
    def __init__(self, message, prediction):
        super().__init__()
        # Create a button for each choice
        for label in ["Ben", "Ayden", "Vince", "Max"]:
            self.add_item(ChoiceButton(label, message, prediction, self))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == TARGET_CHANNEL_ID:
        print(f"{message.author} said: {message.content}")

        # Get prediction from your server
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://127.0.0.1:5000/predict",
                headers={"Message": message.content}
            ) as resp:
                result = await resp.text()
                print(f"HTTP response: {result}")

        prediction = (result.split('"'))[1].capitalize()

        # Send message with buttons
        view = ChoiceView(message, prediction)
        await message.channel.send(
            f"I'm gonna guess... {prediction}!\nAm I right?",
            view=view
        )

    await bot.process_commands(message)

bot.run(TOKEN)
