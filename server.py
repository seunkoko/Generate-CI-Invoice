import os
import requests
import json
from functools import wraps
import mimerender

from flask import Flask, render_template, request

from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__, template_folder='./templates')

# pdf
mimerender.register_mime('pdf', ('application/pdf',))
mimerender = mimerender.FlaskMimeRender(global_charset='UTF-8')

# use template to generate pdf
def render_pdf(html, file_name):
    from xhtml2pdf import pisa
    import io
    # pdf = io.BytesIO()
    result_file = open("{0}.pdf".format(file_name), "w+b")

    pisa_status = pisa.CreatePDF(html, dest=result_file)
    result_file.close()
    return pisa_status


# dummy route
@app.route('/')
def hello_world():
    return 'Hello, World!'

def ci_request(url):
    response = requests.get(url)

    return response.json()

# get/generate invoice route
@app.route('/invoice', methods=['GET'])
def view_invoice():
    url = os.getenv('URL')
    if not url:
        return {
            'status': 'fail',
            'message': 'Url not found in environment variables.'
        }, 400

    invoice_number = os.getenv('INVOICE_NUMBER')
    invoice_month_year = os.getenv('INVOICE_MONTH_YEAR')
    invoice_date = os.getenv('INVOICE_DATE')
    fullname = os.getenv('FULLNAME')
    address = os.getenv('ADDRESS')
    city = os.getenv('CITY')
    state = os.getenv('STATE')
    country = os.getenv('COUNTRY')
    phone = os.getenv('PHONE') 
    email = os.getenv('EMAIL')
    if not invoice_number or not invoice_date or not invoice_month_year \
    or not fullname or not address or not city or not state or not country \
    or not phone or not email:
        return {
            'status': 'fail',
            'message': 'Required user and invoice details not found in environment variables.'
        }, 400

    user_details = {}
    user_details['invoice_number'] = invoice_number
    user_details['invoice_month_year'] = invoice_month_year
    user_details['invoice_date'] = invoice_date
    user_details['fullname'] = fullname
    user_details['address'] = address
    user_details['city'] = city
    user_details['state'] = state
    user_details['country'] = country
    user_details['phone'] = phone
    user_details['email'] = email

    response = ci_request(url)
    if response['status'] == 'empty':
        return {
            'status': 'fail',
            'message': 'No sessions found.'
        }, 400

    html = render_template(
        'invoice.html',
        user_details= user_details,
        monthly_report=response
    )

    file_name = "{0} - {1}".format(user_details['fullname'], user_details['invoice_month_year'])
    render_pdf(html, file_name)

    return {
        'status': 'success',
        'message': 'parsed successfully'
    }, 200 
