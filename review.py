import asyncio
import discord
from discord import app_commands

if __name__ == "__main__" and hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

intents = discord.Intents.all()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_typing = True
intents.typing = True

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.products = [""]
        self.product_mandatory = False
        self.TOKEN = 'TOKEN HERE !!'
        self.guild_id = None

    async def setup_hook(self):
        if self.guild_id:
            self.tree.copy_global_to(guild=discord.Object(id=self.guild_id))
            await self.tree.sync(guild=discord.Object(id=self.guild_id))

client = MyClient(intents=intents)

@client.event
async def on_ready():
    global target_channel

    if client.guilds:
        client.guild_id = client.guilds[0].id
        print(f'Bot is connected to the guild: {client.guilds[0].name} (ID: {client.guild_id})')
    

    print('Logged in as {0.user}'.format(client))

@client.tree.command()
@app_commands.describe(
    product="Product to add or remove.",
    mandatory="Is the product selection mandatory in the review command?"
)
async def setup_product(
    interaction: discord.Interaction,
    product: str,
    mandatory: bool
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    if product not in client.products:
        client.products.append(product)
        action = "added"
    else:
        client.products.remove(product)
        action = "removed"

    client.product_mandatory = mandatory

    embed = discord.Embed(title="Setup Complete", color=discord.Color.green())
    embed.add_field(name="Action", value=f"Product '{product}' {action}.", inline=False)
    embed.add_field(name="Mandatory", value=f"Product selection is {'mandatory' if mandatory else 'optional'}.", inline=False)
    embed.add_field(name="Current Products", value=", ".join(client.products), inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

async def product_autocomplete(
    interaction: discord.Interaction,
    current: str
):
    products = client.products  
    return [
        app_commands.Choice(name=product, value=product)
        for product in products if current.lower() in product.lower()
    ]

@client.tree.command()
@app_commands.describe(
    number="Enter a number of stars between 1 and 5.",
    image_link="Provide a link to an image.",
    product="Select a product.",
    message="Write your review."
)
@app_commands.autocomplete(product=product_autocomplete)
async def review(
    interaction: discord.Interaction,
    number: app_commands.Range[int, 1, 5],  
    image_link: str,
    message: str,
    product: str = ""  
):
    products = client.products

    if product and product not in products:
        await interaction.response.send_message(
            f"Please choose a valid product from the list: {', '.join(products)}.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        description=f"\n :bookmark_tabs: Feedback :bookmark_tabs: \n```{message}\n```",
        color=discord.Color.blue()
    )
    stars = '⭐' * number
    embed.add_field(name="Rating", value=stars, inline=False)
    embed.set_image(url=image_link)
    custom_message = f"{interaction.user.mention}"
    embed.set_thumbnail(url=interaction.user.avatar.url)
    if product:
        embed.add_field(name="Product", value=product, inline=False)
    embed.set_author(
        name=f"Review by {interaction.user.display_name}",
        icon_url=interaction.user.avatar.url
    )
    await interaction.response.send_message(content=custom_message, embed=embed)

async def product_autocomplete(
    current: str
):
    products = client.products  
    return [
        app_commands.Choice(name=product, value=product)
        for product in products if current.lower() in product.lower()
    ]

client.run(client.TOKEN)
