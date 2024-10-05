import discord
from discord.ext import commands
from utils.views.donateViews import donateView

class donate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="aimcolor")
    async def donate_command(self, ctx):
        await ctx.message.delete()
        view = donateView()
        embed = discord.Embed(
            title="Aimcolor",
            description="100% indetectável, aim assist com config pronta para uso legit.",
            color=discord.Color.blurple()
        )
        embed.set_image(url = self.bot.user.avatar.url)
        embed.set_author(name = self.bot.user.name, icon_url = self.bot.user.avatar.url)
        embed.set_footer(text = f"Suporte garantido. Envio rápido e automático com instruções para uso!")
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(donate(bot))