from downshift import constants

parser = constants.Amtrak

class Address:

    def __init__(self, address1: str, address2: str, city: str, state: str, zip_code: str):
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip_code = zip_code

    def parse(data: dict):
        return Address(
            parser.addr1(data),
            parser.addr2(data),
            parser.city(data),
            parser.state(data),
            parser.zip(data))
    
    def string(self):
        addr1 = self.address1.strip()
        addr2 = self.address2.strip()
        city = self.city
        state = self.state
        zip_code = self.zip_code

        if addr2: addr1 += ' '

        return f'{addr1}{addr2}, {city} {state} {zip_code}'

    def __str__(self):
        return f'<Address {self.string()}>'