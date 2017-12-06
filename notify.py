from twilio.rest import Client

class Notifier:
    def __init__(self, filename='etc/.twilio'):
        with open('etc/.twilio', 'r') as infile:
            lines = [str(line).strip() for line in infile]
        assert len(lines) == 4, 'Require four lines in etc/.twilio'
        sid   = lines[0]
        token = lines[1]

        self.to    = lines[2]
        self.from_ = lines[3]

        self.client = Client(sid, token)

    def notify(self, body):
        self.client.api.account.messages.create(
            to=self.to,
            from_=self.from_,
            body=body)

