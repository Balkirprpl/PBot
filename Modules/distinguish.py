import re
from Modules.colors import red, blue, reset
SHORT_LINKS = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'buff.ly',
            'adf.ly', 'is.gd', 'cutt.ly', 'shorte.st'
            ]



def load_bad_words():
        with open("Modules/words.txt", 'r', encoding='utf-8') as file:
            bad_words = set(word.strip().lower() for word in file.readlines())
        return bad_words



BAD_WORDS_SET = load_bad_words()

def further_analysis(bot):
    # checking for shortened links in comments
    # possible fishing bot
    print(f"{blue}Checking links.{reset}")
    n_links, n_short_links = check_links(bot)
    print(f"{bot.name} has {n_links} links and {n_short_links} shortened links")
    if n_short_links > 0 or n_links > 1:
        bot.add_reason(f"{bot.name}:{bot.ID} was caught sending shortened links")

    # checking for profanity
    # possible harrasing bot
    print(f"{blue}Checking for profanity.{reset}")
    profanity = count_bad_words(bot)
    print(f"This account has used profanity {profanity} times")
    if profanity >= 300:
        bot.add_reason(f"{bot.name}:{bot.ID} was caught possibly harrassing another user")

    # checking opt-out or autodeclared bot
    # checking for good bots
    declared_bot = is_declared_bot(bot)
    print(f"is this account a autodeclared bot? {blue+str(declared_bot)+reset if declared_bot else red+str(declared_bot)+reset }")
    if declared_bot:
        bot.set_good()
    print()
    return bot


def find_links(text):
    pattern = r'\b(?:http://|https://|www\.|goo\.gl/|tinyurl\.com/|bit\.ly/)\S+\.\S+'
    links = re.findall(pattern, text)
    return links


def check_links(bot):
    n_links = 0
    n_short_links = 0
    all_comments = bot.user.comments.new(limit=None)
    for comment in all_comments:
        # print(f"links: {find_links(comments.body)}")
        # algorithm to check shortened links done but
        # make a request to see if the link is shortened?
        # res code 3xx == shortened link
        links_in_comments = find_links(comment.body)
        if len(links_in_comments) > 0:
            n_links += len(links_in_comments)
            for link in links_in_comments:
                if is_shortened_link(link):
                    n_short_links += 1
        return n_links, n_short_links

def is_shortened_link(url):
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return domain in SHORT_LINKS

def is_declared_bot(bot):
    auto_declared = False
    if 'bot' in bot.name.lower():
        return True
    for comment in bot.user.comments.new(limit=5):
        if 'i am a bot' in comment.body.lower():
            auto_declared = True
    return auto_declared

def count_bad_words(bot):
    comments = bot.user.comments.new(limit=None)
    bad_word_count = 0
    for comment in comments:
        # split comment into all comments
        comment_words = comment.body.lower().replace('|',' ').split()
        # sum all the occurences of a bad word in the comment
        for word in comment_words:
            if word in BAD_WORDS_SET:
                bad_word_count += 1

    return bad_word_count

