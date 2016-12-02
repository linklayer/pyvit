import json
from .. import bus


class JsonDbParser():
    def parse(self, filename):
        with open(filename, 'r') as f:
            db = json.load(f)

            # create a bus for this database
            b = bus.Bus()
            for msg in db['messages']:
                # create a message
                m = bus.Message(msg['name'], int(msg['id'], 0))

                # iterate over signals
                for start_bit, sig in msg['signals'].items():
                    # create a signal
                    s = bus.Signal(sig['name'], sig['bit_length'])

                    # parse offset and factor if set
                    if 'offset' in sig:
                        s.offset = int(sig['offset'])
                    if 'factor' in sig:
                        s.factor = int(sig['factor'])

                    # add this signal to the message
                    m.add_signal(s, int(start_bit))

                # add this message to the bus
                b.add_message(m)

        return b
