#!/usr/bin/env python3
"""
Subscription Web App - Flask frontend for Stripe subscriptions
"""
from flask import Flask, render_template, request, jsonify, redirect
import os
from subscription_manager import create_checkout_session, handle_successful_payment, CITY_PRODUCTS

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Stripe keys
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')


@app.route('/')
def index():
    """Main subscription page with all cities"""
    return render_template('subscription_index.html', 
                          stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout():
    """Create Stripe checkout session"""
    try:
        data = request.get_json()
        city = data.get('city')
        email = data.get('email')
        
        if not city or not email:
            return jsonify({'error': 'Missing city or email'}), 400
        
        if city not in CITY_PRODUCTS:
            return jsonify({'error': 'Invalid city'}), 400
        
        # Create checkout session
        session = create_checkout_session(
            city=city,
            user_email=email,
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel'
        )
        
        return jsonify({'id': session.id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


def cancel():
    """Handle cancelled payment"""
    return redirect('/')


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhooks"""
    import stripe
    
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # Handle events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session['id'])
    
    elif event['type'] == 'customer.subscription.deleted':
        # Handle cancellation
        subscription = event['data']['object']
        # TODO: Mark subscription as cancelled in database
        pass
    
    return jsonify({'status': 'success'})


@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("="*70)
    print("🌐 CONTRACTOR LEADS - SUBSCRIPTION APP")
    print("="*70)
    print(f"   Open: http://localhost:5002")
    print("="*70)
    
    app.run(host='0.0.0.0', port=5002, debug=True)
