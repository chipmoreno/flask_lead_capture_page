from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
from dotenv import load_dotenv
from flask_cors import CORS
CORS(app)
import re
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.environ.get('api_key')
api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')
PHONE_REGEX = re.compile(r'^\+\d{1,15}$')

import os
load_dotenv()
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/submit-email', methods=['POST'])
def submit_email():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        whatsapp_number = request.form.get('whatsapp_number')

        if not email or not EMAIL_REGEX.match(email):
            return "Invalid email format. Please provide a valid email address.", 400
        
        if not first_name:
            return "Please provide your first name.", 400

        sanitized_whatsapp_number = re.sub(r'[.\s-]', '', whatsapp_number)
        
        if not sanitized_whatsapp_number or not PHONE_REGEX.match(sanitized_whatsapp_number):
            return "Invalid WhatsApp number format. Please include a country code, e.g., +1234567890.", 400
        
        sanitized_email = email.strip().replace('\n', '').replace('\r', '')
        
        create_contact = sib_api_v3_sdk.CreateContact(
            email=sanitized_email,
            attributes={'FIRSTNAME': first_name, 'SMS': sanitized_whatsapp_number},
            list_ids=[3]
        )
        
        try:
            api_response = api_instance.create_contact(create_contact)
            return redirect(url_for('thank_you'))
        except ApiException as e:
            return f"An API error occurred: {e}", 500

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)

