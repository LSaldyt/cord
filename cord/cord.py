import datetime, pickle, time, sys, os

from contextlib import contextmanager

from .notify import Notifier

@contextmanager
def retrieve(database, name, default):
    element = database.get(name, default)
    yield element
    database[name] = element

class Cord:
    def __init__(self, commandTree, save_data, status):
        self.commandTree = commandTree
        self.save_data   = save_data
        self.status      = status

    def respond(self, database, notifyClient):
        with retrieve(database, 'checked', set()) as checked:
            for message in notifyClient.client.messages.list():
                if message.direction == 'inbound':
                    sent = message.date_sent
                    now  = datetime.datetime.utcnow()
                    today  = sent.day == now.day
                    hour   = sent.hour == now.hour
                    minute = abs(sent.minute - now.minute) < 2
                    if today and hour and minute and message.sid not in checked:
                        checked.add(message.sid)
                        command, *args = message.body.strip().lower().split(' ')
                        print('Recieved command: {} {}'.format(command, ' '.join(args)))
                        if command in self.commandTree:
                            self.commandTree[command](database, notifyClient, *args)
                        else:
                            print('Invalid command: {}'.format(command))

    def loop(self):
        notifyClient  = Notifier()

        datafile = '.data.pkl'

        if os.path.isfile(datafile):
            with open(datafile, 'rb') as infile:
                database = pickle.load(infile)
        else:
            database = dict()
        try:
            print('Waiting...', end='', flush=True)
            with retrieve(database, 'checked', set()) as checked:
                while True:
                    self.save_data(database)
                    self.respond(database, notifyClient)
                    self.status(database)
                    time.sleep(.1)
                    print('.', end='', flush=True)
        finally:
            with open(datafile, 'wb') as outfile:
                pickle.dump(database, outfile)

def main(args):
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
