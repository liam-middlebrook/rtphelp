from flask import Flask, request, redirect
import twilio.twiml
from twilio.rest import TwilioRestClient
import configparser
import random

from CSHLDAP import CSHLDAP

app = Flask(__name__)

# Load config file
config = None
with open("config") as config_file:
    config = configparser.ConfigParser()
    config.read_file(config_file)

# get twilio auth creds
account_sid = config.get('twilio', 'account_sid')
account_secret = config.get('twilio', 'account_secret')
account_phone = config.get('twilio', 'account_phone')
# get list of rtps and phone numbers
rtp_list = config.get('rtp', 'list')
rtp_list = rtp_list.split(',')

ldap_user = config.get('ldap', 'user')
ldap_password = config.get('ldap', 'password')

ldap = CSHLDAP(ldap_user, ldap_password)


@app.route("/", methods=['POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""

#    rtp = random.choice(rtp_list).split(':')
#    rtp_name = rtp[0]
#    rtp_num = rtp[1]
#    client = TwilioRestClient(account_sid, account_secret)
#    message = client.messages.create(to=rtp_num, from_=account_phone, body=request.form['Body'])
    message = client.messages.create(to=rtp_num, from_=account_phone, body=str(ldap.member(request.form['Body'])))

    resp = twilio.twiml.Response()
    resp.message("Messaged " + rtp_name)
    return str(resp)

def main():
    app.run(debug=True, port=6969)

if __name__ == "__main__":
    main()
