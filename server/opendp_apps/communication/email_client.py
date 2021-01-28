import os

from sendgrid import sendgrid, Email, Content, Mail, To


class SendGridAPIError(Exception):
    pass


class EmailClient(object):

    # TODO: Make this a product-wide address.
    # To verify a new account:
    #   1. Go to https://app.sendgrid.com/settings/sender_auth/senders
    #   2. Click "verify new sender" and proceed
    default_from_email = 'kraffmilleropendptest@gmail.com'

    def __init__(self, from_email=None, api_key=None):
        self.from_email = from_email if from_email else self.default_from_email
        if not api_key:
            try:
                # Can't just use .get() here because the key may be an empty string, which would be returned
                self.api_key = os.environ['SENDGRID_API_KEY'] \
                    if os.environ.get('SENDGRID_API_KEY') \
                    else 'sendgrid-api-key-not-set'
            except KeyError:
                raise SendGridAPIError("SENDGRID_API_KEY must be passed as an argument or"
                                       " set as an environment variable")
        else:
            self.api_key = api_key
        self.sendgrid_client = sendgrid.SendGridAPIClient(self.api_key)

    def send(self, to_email=None, subject=None, content=None, content_type=None):
        from_email = Email(self.from_email)
        to_email = To(to_email)
        content = Content(content_type, content)
        mail = Mail(from_email, to_email, subject, content)
        return self.sendgrid_client.client.mail.send.post(request_body=mail.get())


if __name__ == '__main__':
   # apikey_message = "Current API Key: " + os.environ.get('SENDGRID_API_KEY')
   # print("-"*(len(apikey_message)+1))

  #  print("Current API Key: ", os.environ.get('SENDGRID_API_KEY'))
    c = EmailClient()
    print("From Email: ", c.from_email)
 #   print("-"*(len(apikey_message)+1))
    result = c.send(to_email='ellen.kraffmiller@gmail.com', subject='test test',
                    content='hi', content_type='text/plain')
    print("Message Sent")
    print("Status Code: ", result.status_code)
  #  print("-"*(len(apikey_message)+1))
