link = "https://www.reddit.com/user/"
cyan = '\033[34m'
reset = '\033[37m'

def decide(account, ignore_list):
    if 'exiting' in ignore_list:
        print(f"url: {cyan}{link}{account.name}{reset}")
        return True
    if 'all' in ignore_list or account.good_bot:
        return False
    if account.good_bot == '0' and not 'good' in ignore_list:
        print(f"Autodeclared bot usually not harmful.")
        x = input("Want to report? (y?) (0 to ignore all)")
        if x.rstrip().lower() == 'y':
            print(f"url: {cyan}{link}{account.name}{reset}")
            return True
    else:
        if len(account.reasons) > 0:
            print(f"url: {cyan}{link}{account.name}{reset}")
            return True
        elif not 'inconclusive' in ignore_list:
            print(f"No decisive reason to report this bot.")
            z = input("Want to report? (y?)")
            if z.rstrip().lower() == 'y':
                print(f"url: {cyan}{link}{account.name}{reset}")
    return False
