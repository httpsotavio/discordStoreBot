import stripe
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from flask import Flask, request
from utils.utils import addTransaction
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

stripeApp = Flask(__name__,
                  static_url_path="",
                  static_folder="")


@stripeApp.route('/webhook', methods=['POST'])
def stripeWebhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        channel = session.get('metadata', {}).get("channel")
        user = session.get('metadata', {}).get("user")
        amount = session.get('metadata', {}).get("amount")
        productIndex = session.get('metadata', {}).get("product")
        productName = session.get('metadata', {}).get("productName")
        productDescription = session.get('metadata', {}).get("productDescription")

        addTransaction(channel=channel, user=user, amount=amount, productIndex=productIndex, productName=productName, productDescription=productDescription)
        print(f"Pagamento realizado com sucesso. Produto: {session.get('metadata', {}).get('productDescription')}")
    return "", 200

stripeApp.run(port=4242)
