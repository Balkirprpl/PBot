link = "https://www.reddit.com/user/"

def decide(account, x, z):
    if account.good_bot and x.rstrip() == '0':
        print(f"Autodeclared bot usually not harmful.")
        x = input("Want to report? (y?) (0 to ignore all)")
        if x.rstrip().lower() == 'y':
            print(f"{link}{account.name}")
            return True
    else:
        if len(account.reasons) > 0:
            print(f"{link}{account.name}")
            return True
        elif z.rstrip() == '0':
            print(f"No decisive reason to report this bot.")
            z = input("Want to report? (y?) (0 to ignore all)")
            if z.rstrip().lower() == 'y':
                print(f"{link}{account.name}")
    return False
