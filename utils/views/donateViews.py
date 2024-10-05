import discord
from discord.ui import Button, View, Select
import utils.utils as utils
import asyncio

plans = {
    "aimcolor30d": {"title": "Aimcolor 30 dias", "value": 100},
    "aimcolor15d": {"title": "Aimcolor 7 dias", "value": 50},
    "aimcolor7d": {"title": "Aimcolor trial 1 dia", "value": 15},
}



class donateView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(selectPlan())

class ChannelCreationView(View):
    def __init__(self, channelUrl):
        super().__init__(timeout=None)
        self.add_item(Button(label="Acessar o canal", url=channelUrl, style=discord.ButtonStyle.link))

class ChannelMenuView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    
    async def reactivateButton(self, button: Button, message: discord.Message):
        await asyncio.sleep(900)

        button.disabled = False

        await message.edit(view=self)

    @discord.ui.button(label="Continuar compra", style=discord.ButtonStyle.green, custom_id="continuepurchase")
    async def continuePurchasebutton(self, interaction: discord.Interaction, button: Button):
        button.disabled = True
        await interaction.response.edit_message(view=self)

        interaction.client.loop.create_task(self.reactivateButton(button, interaction.message))

        embed = interaction.message.embeds[0]
        footerText = embed.footer.text
        plan = plans[footerText]
        if(plan):
            url = utils.createCheckoutSession(plan["title"], f"Valor: R${plan["value"]}", plan["value"], footerText, interaction.channel.id, interaction.guild.id, interaction.user.name)
            embed = discord.Embed(
                title="Quase lá! 😚",
                description=f"[Clique aqui para ser redirecionado para a plataforma que cuidará do processo de pagamento]({url})",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Seus dados estão seguros, todo o processo de pagamento é processado pela plataforma Stripe.\nO produto será enviado no canal logo após a confirmação do envio ser realizada pela plataforma.")
            embed.set_image(url="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXo3YzQzcGdnNmk5ZWR3NnljZmsyZGg2bzNrdWs2cXFob2c1MGN4YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7btMCltyDvSgF92E/giphy.webp")

            await interaction.channel.send(embed=embed)
        else:
            await interaction.followup.send("Error with productid.")
            

    @discord.ui.button(label="Fechar ticket", style=discord.ButtonStyle.danger, custom_id="closeticket")
    async def deleteChannelButton(self, interaction: discord.Interaction, button: Button):
        userOverwrite = interaction.channel.overwrites_for(interaction.user)
        if  userOverwrite.send_messages == True:
            await interaction.channel.delete(reason=f"Ticket fechado por {interaction.user}")
        else:
            await interaction.response.send_message("Você não tem permissão para deletar este canal.", ephemeral=True)

class selectPlan(Select):
    def __init__(self):
        options = []

        for plan_key, plan_data in plans.items():
            option = discord.SelectOption(
                label=plan_data["title"],
                description=f"{plan_data["value"]}R$",
                value=plan_key
            )
            options.append(option)

        super().__init__(placeholder="Assinaturas disponíveis", min_values=1, max_values=1, options=options, custom_id="selectplan")

    async def callback(self, interaction: discord.Interaction):
        categoryName = "🛒| Carrinho"
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=categoryName)
        if category is None:
            await interaction.response.send_message("Error! Contact an admin.")
            return
        

        channelName = f"📝{utils.formatString(interaction.user.name)}" 
        for channel in category.text_channels:
            if channelName in channel.name:
                await interaction.response.send_message("Você já tem um ticket em aberto, feche ele para poder abrir outro.", ephemeral=True)
                return
            
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        newChannel = await guild.create_text_channel(name=channelName, category=category, overwrites=overwrites)
        channelUrl = f"https://discord.com/channels/{guild.id}/{newChannel.id}"
        plan = plans[self.values[0]]
        view = ChannelCreationView(channelUrl)
        channelMenuView = ChannelMenuView()

        embed = discord.Embed(
            title="Ticket de compra",
            description=f"Produto: {plan["title"]}\nValor: R${plan["value"]}",
            color=discord.Color.blurple()
        )

        embed.set_footer(text = f"{self.values[0]}")

        await newChannel.send(view=channelMenuView, embed=embed)
        await interaction.response.send_message("Canal criado com sucesso. Para dar continuidade na compra, clique no botão abaixo para ser redirecionado.", view=view, ephemeral=True)