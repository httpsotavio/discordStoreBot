import re
import stripe
import sqlite3
import os
import datetime
import random
import string

from dotenv import load_dotenv

load_dotenv()

dbPath = os.path.join(os.path.dirname(__file__), '../server/database.db')
# conn = sqlite3.connect(dbPath)
# cursor = conn.cursor()

# cursor.execute(f"""
# CREATE TABLE IF NOT EXISTS transactions (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     channel INTEGER NOT NULL,
#     user INTEGER NOT NULL,
#     productName TEXT NOT NULL,
#     productDescription TEXT NOT NULL,
#     amount TEXT NOT NULL,
#     productIndex TEXT NOT NULL,
#     completed INTEGER NOT NULL DEFAULT 0,
#     date TEXT NOT NULL
# )
# """)

# conn.commit()
# conn.close()

from utils.views.donateViews import ChannelMenuView, donateView

stripe.api_key = os.getenv("STRIPE_API_KEY")


def formatString(string: str) -> str:
    # Substitui os caracteres que o Discord normalmente remove ou altera
    return re.sub(r"[^a-zA-Z0-9-_]", "", string) 


async def registerViews(bot):
    bot.add_view(ChannelMenuView())
    bot.add_view(donateView())

def createCheckoutSession(productName, productDescription, amount, productIndex, channelId, guildId, user):
    try:
        product = stripe.Product.create(
            name=productName,
            description=productDescription
        )

        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount * 100,
            currency="brl"
        )

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price.id,
                    "quantity": 1,
                },
            ],
            metadata={
                "productName": productName,
                "productDescription": productDescription,
                "amount": amount,
                "product": productIndex,
                "channel": channelId,
                "guild": guildId,
                "user": user
            },
            mode="payment",
            success_url="https://google.com",  # Página de sucesso
            cancel_url="https://google.com",    # Página de cancelamento
        )

        return checkout_session.url
    except Exception as e:
        return str(e)
    

def addTransaction(channel, user, productName, productDescription, amount, productIndex):
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    date = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M")
    cursor.execute(f"""
    INSERT INTO transactions (channel, user, productName, productDescription, amount, productIndex, date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (channel, user, productName, productDescription, amount, productIndex, date))
    conn.commit()
    conn.close()

def getUncompletedTransactions():
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE completed = 0")
    rows = cursor.fetchall()
    conn.close()
    return rows


def setTransactionCompleted(id):
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET completed = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def generateRandomProductKey():
    letters = "".join(random.choices(string.ascii_letters, k=15))  # 15 letras
    numbers = "".join(random.choices(string.digits, k=15))         # 15 números
    
    random_key = letters + numbers
    
    random_key = "".join(random.sample(random_key, len(random_key)))
    
    return random_key