from dukpt import Server as DukptServer, InvalidDUKPTArguments
from Crypto.Cipher import DES3
from bitstring import BitArray

class CardReader:
    DEFAULT_SESSION_KEY = BitArray(hex="00000000000000FF00000000000000FF")

    def __init__(self):
        self.device_serial = None
        self.card_swipe = None

    @staticmethod
    def prompt_input(prompt):
        return input(prompt + ": ")

    def get_data(self):
        decrypted_data = self.decrypt_data()
        return decrypted_data

    def decrypt_data(self):
        bdk = BitArray(hex=self.prompt_input("DECRYPTION_KEY"))
        result = {}

        if not bdk:
            return result

        try:
            dukpt = DukptServer(bdk=bdk.bytes)
            ksn = BitArray(hex=self.card_swipe['card_data'].get("KSN"))
            ipek = dukpt.generate_ipek(ksn=ksn)
            session_key = dukpt.derive_key(ksn=ksn, ipek=ipek) ^ self.DEFAULT_SESSION_KEY

            data = BitArray(hex=self.card_swipe['card_data'].get('Track1'))
            cipher = DES3.new(session_key.bytes, DES3.MODE_CBC, BitArray(hex="0000000000000000").bytes)
            decrypted = cipher.decrypt(data.bytes)

            track1 = self.bit_to_string(decrypted).split("^")

            if len(track1) > 1:
                result = self.parse_decrypted_data(track1)

        except (InvalidDUKPTArguments, ValueError, AttributeError):
            pass

        return result

    @staticmethod
    def bit_to_string(data):
        return str(data).replace("b'", "'")

    def parse_decrypted_data(self, data):
        parsed_data = {}

        try:
            card_number = data[0].split("%B")[1]
            exp_year, exp_month = data[2][:2], data[2][2:4]

            parsed_data = {
                "DecryptedCardSwipe": {
                    "card_number": card_number,
                    "name": self.get_card_name(),
                    "exp_month": exp_month,
                    "exp_year": exp_year,
                }
            }

        except IndexError:
            pass

        return parsed_data

    def get_card_name(self):
        name = self.card_swipe['additional_data'].get('CardName', '').strip()

        if name.endswith('/'):
            name = name.replace('/', '')
            name = name.strip()

        if '/' in name:
            name = ' '.join(reversed([i.strip() for i in name.split('/')])).strip()

        return name

    def get_card_swipe(self):
        self.device_serial = self.prompt_input("DeviceSerial")
        self.card_swipe = {
            'card_data': {
                'KSN': self.prompt_input('KSN'),
                "MagnePrint": self.prompt_input('MagnePrint'),
                'MagnePrintStatus': self.prompt_input('MagnePrintStatus'),
                'Track1': self.prompt_input('Track1'),
                'Track2': self.prompt_input('Track2'),
                'Track3': self.prompt_input('Track3'),
                'KeyType': 0
            },

            'additional_data': {
                'CardExpDate': self.prompt_input('CardExpDate'),
                'CardName': self.prompt_input('CardName'),
                'CardPANLength': self.prompt_input('CardPANLength'),
                'EncryptionStatus': self.prompt_input('EncryptionStatus')
            }
        }

    def main(self):
        self.get_card_swipe()
        result = self.get_data()
        print(result)

if __name__ == "__main__":
    cr_obj = CardReader()
    cr_obj.main()
