import discord
import os

from dotenv import load_dotenv
from discord.ext import commands, tasks
from colorama import Fore

from utils.utils import registerViews, getUncompletedTransactions, setTransactionCompleted, generateRandomProductKey

load_dotenv()

class Bot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
    
    async def on_ready(self):
        print(Fore.BLUE + f"Bot conectado como {self.user}")
        await registerViews(self)
        await self.load_extensions()
        self.check_for_completed_transactions.start()

    async def load_extensions(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

    @tasks.loop(seconds=10) 
    async def check_for_completed_transactions(self):
        rows = getUncompletedTransactions()
        if rows:
            for row in rows:
                print(Fore.BLUE + f"Encontrado registro incompleto: {row}")
                channel_id = row[1]

                channel = self.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(
                        title="Pagamento aprovado!",
                        description=f"Constatamos a aprovação do pagamento, diante disso, estaremos lhe enviando uma chave de uso único para que você use na liberação do programa, lembrando que após utilizar esta chave, seu HWID será salvo pelo programa, não conseguindo cadastrá-la em outro computador, então, cuidado quando for utilizá-la. USO ÚNICO! \nKey: {generateRandomProductKey()} (ficticia, isso funciona ainda nam)",
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text="Obrigado pela preferência! 😊\nSuporte 24horas ativo 📝🔥")
                    await channel.send(embed=embed)
                    setTransactionCompleted(row[0])
                    print(Fore.GREEN + "Produto enviado.")
                    

intents = discord.Intents.default()
intents.message_content = True

bot = Bot(command_prefix='/', intents=intents)


if __name__ == '__main__':
    # print("token: "+os.getenv("TOKEN"))
    bot.run(os.getenv("TOKEN"))