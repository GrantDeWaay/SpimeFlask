import random

import rsa


# First the current holder of the package will send
# a API call to create a transaction he will provide:
#	-The package they want to send
#	-The destination they want to sent it to
def create_keypair():
	return rsa.newkeys(128)


def create_key(sender, recipient):
	(pubkey, privkey) = rsa.newkeys(512)
	noice = str(random.randint(9999999, 100000000))
	message = noice.encode('utf8')
