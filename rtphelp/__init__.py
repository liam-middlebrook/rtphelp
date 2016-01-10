from flask import Flask, request, redirect
import twilio.twiml
from twilio.rest import TwilioRestClient
import configparser
import random
import re

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

# get ldap info
ldap_user = config.get('ldap', 'user')
ldap_password = config.get('ldap', 'password')

# query lists
phones = None
rtp_list = None

def memberIsActive(member):
    return 'active' in member and '0' not in member['active']

def getPhoneUserList(userList, active=False):
    phonez = [{'name': m['cn'], 'number': m['mobile']} for m in userList if
'mobile' in m and (not active or memberIsActive(m))]
    for person in phonez:
        if isinstance(person['name'], list):
            person['name'] = person['name'][0]
        if isinstance(person['number'], list):
            person['number'] = person['number'][0]
        person['number'] = re.sub('[^\d\n]', '', person['number'])
    return phonez
    
@app.route("/", methods=['POST'])
def hello_monkey():

    # Check That Request Is Coming From Twilio
    if request.form['AccountSid'] != account_sid:
        print("Error: User Not Twilio!")
        print(request.form)
        return "Error: You Don't Appear to Be Twilio!"

    # Pick a Random Active RTP to Bother
    rtp = random.choice(rtp_list)
    rtp_name = rtp['name']
    rtp_num = rtp['number']

    # Verify Sender
    sender = request.form['From'][2:]
    sender_exists = False
    for p in phones:
        if p['number'] in sender and p['number'] is not '':
            print(p['name'])
            sender = p['name']
            sender_exists = True
            break
    if not sender_exists:
        print("Error: User Not In LDAP!")
        print(sender)
        resp = twilio.twiml.Response()
        resp.message("Error: You Have Not Registered Your Phone in LDAP!")
        return str(resp)

    # Prepare the Message
    client = TwilioRestClient(account_sid, account_secret)
    help_request = request.form['Body']
    print("To: %s\nFrom: %s\nBody:\n%s\n" % (rtp_name, sender, help_request))
    message_text = help_request + "\nFrom: " + sender

    message = client.messages.create(to=rtp_num,
        from_=account_phone, body=message_text)
    resp = twilio.twiml.Response()
    resp.message("Messaged " + rtp_name)
    return str(resp)

def main():
    global phones
    global rtp_list

    ldap = CSHLDAP(ldap_user, ldap_password)

    phones = getPhoneUserList(ldap.members())

    # get active RTPs
    rtp_list = getPhoneUserList([rtp[1] for rtp in ldap.rtps()], True)
    app.run(debug=True, host='0.0.0.0', port=6969)

if __name__ == "__main__":
    main()
