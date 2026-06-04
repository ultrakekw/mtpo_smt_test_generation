###################################################################################
# If we do not unwrap arguments of the function getaddrinfo in line 901 of the file
# /usr/lib/python3.8/socket.py in our program, it can be done only by adding unwrap
# statements "host = unwrap(host); port = unwrap(port)" into the first line of that
# function manually.
#
# If we do not avoid wrapping the file ".venv/lib/python3.8/site-packages/rpyc/core/brine.py",
# then the statement "return IMM_INTS_LOADER[tag]" in line 357 of that file should
# also be replaced with the unwrapping "return int.__int__(IMM_INTS_LOADER[tag])"!
###################################################################################

import rpyc

def startswith(x, prefixes):
    while x > 0:
        if x in prefixes: return True
        x //= 10
    return False

# https://en.wikipedia.org/wiki/Payment_card_number#Issuer_identification_number_(IIN)
def client(x): #(x: int) -> str:
    proxy = rpyc.connect("localhost", 8080).root
    if proxy:
        if pow(10, 15-1) <= x and proxy.check_luhn(x):
            if pow(10, 16-1) <= x:
                if x < pow(10, 19):
                    if startswith(x, range(3528, 3590)):
                        return 'JCB'
                    if x < pow(10, 16) and (startswith(x, range(51, 56)) or startswith(x, range(2221, 2721))):
                        return 'Mastercard'
            elif startswith(x, (34, 37)):
                return 'American Express'
        return 'Unknown'
    return 'Server Error'
