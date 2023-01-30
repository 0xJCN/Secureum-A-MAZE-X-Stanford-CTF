from ape import chain

MAX_UINT256 = 2**256 - 1

w3 = chain.provider.web3


def set_balance(account, amount):
    chain.set_balance(account, amount)


def time_travel(time_in_seconds):
    time = chain.pending_timestamp + time_in_seconds
    chain.mine(1, time)


def get_balance(account):
    return chain.provider.get_balance(account)


def get_code(account):
    return chain.provider.get_code(w3.toChecksumAddress(account)).hex()


def get_timestamp():
    return chain.pending_timestamp


def get_block():
    return chain.blocks[-1].number
