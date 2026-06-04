import rpyc

class MyService(rpyc.Service):
    def check_luhn(self, value):
        check_sum = 0
        is_even = False
        while value > 0:
            digit = value % 10; value //= 10
            if is_even:
                digit *= 2
                if digit > 10:
                    digit -= 9
            check_sum += digit
            is_even = not is_even
        return check_sum % 10 == 0

if __name__ == "__main__":
    server = rpyc.utils.server.ThreadedServer(MyService, port=8080, protocol_config={'allow_public_attrs': True})
    server.start()
