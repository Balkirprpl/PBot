from keys import key, client, user_agent
from detect2 import scanAccount
from decide import decide
import praw
import datetime
import csv
import os
import re
import spacy
import warnings
import requests
from requests.exceptions import RequestException



reset = '\033[37m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'
cyan = '\033[36m'

current_scan = []

warnings.filterwarnings('ignore', category=UserWarning)

def load_bad_words():
    with open("bad-words.txt", 'r', encoding='utf-8') as file:
        bad_words = set(word.strip().lower() for word in file.readlines())
        return bad_words


DATABASE = "database.csv"
COMMENT_DEPTH = 5
SHORT_LINKS = [
        'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'buff.ly',
        'adf.ly', 'is.gd', 'cutt.ly', 'shorte.st'
        ]
BAD_WORDS_SET = load_bad_words()

file = open(DATABASE, mode='a', newline='')
db = csv.writer(file)
if os.path.getsize(DATABASE) == 0:
    headers = ['user_id','username','link_karma','comment_karma','created','verified','submissions','comments']
    db.writerow(headers)


nlp = spacy.load("en_core_web_md")

class Bot:
    def __init__(self, data):
        self.ID = data[0]
        self.name = data[1]
        self.link_karma = data[2]
        self.comment_karma = data[3]
        self.total_karma = data[4]
        self.birth = data[5]
        self.verified = data[6]
        self.n_submissions = data[7]
        self.n_comments = data[8]

        self.sim_score = -1
        self.lda_score = -1

        self.reasons= []

        self.good_bot = False

    def update_scores(self, new_sim, new_lda):
        self.sim_score = new_sim
        self.lda_score = new_lda

    def set_user(self, user):
        self.user = user

    def add_reason(self, reason):
        self.reasons.append(reason)

    def get_reasons(self):
        return self.reasons

    def set_good(self):
        self.good_bot = True

    def print_bot(self):
        print(f"""Username: {cyan}{self.name}{reset}
Id: {green}{self.ID}{reset}
Link Karma: {blue}{self.link_karma}{reset}
Comment Karma: {blue}{self.comment_karma}{reset}
Total Karma: {yellow}{self.total_karma}{reset}
Account age: {yellow}{self.birth}{reset}
Is verified: {yellow}{self.verified}{reset}
Total submissions: {yellow}{self.n_submissions}{reset}
Total comments: {yellow}{self.n_comments}{reset}
{'Detected reasons: '+ red if len(self.reasons) > 0 else ''}
{self.reasons if len(self.reasons) > 0 else ''}
{green + 'This is a good bot' + reset if self.good_bot else reset}""")



def compare_text(text1, text2):
    similarity = nlp(text1).similarity(nlp(text2))
    return similarity

def print_comments(user):
    for comments in user.comments.new(limit=None):
        print(comments.body)

def add_to_db(data):
    db.writerow(data)

def print_account(data):
    print(f"""Username: {cyan}{data[1]}{reset}
Id: {green}{data[0]}{reset}
Link Karma: {blue}{data[2]}{reset}
Comment Karma: {blue}{data[3]}{reset}
Total Karma: {yellow}{data[4]}{reset}
Account age: {yellow}{data[5]}{reset}
Is verified: {yellow}{data[6]}{reset}
Total submissions: {yellow}{data[7]}{reset}
Total comments: {yellow}{data[8]}{reset}
""")

def find_links(text):
    pattern = r'\b(?:http://|https://|www\.|goo\.gl/|tinyurl\.com/|bit\.ly/)\S+\.\S+'
    links = re.findall(pattern, text)
    return links

def scan_comments(comment_similarity_array):
    # ------------------------------
    #   Calculating txt similarity
    # ------------------------------
    z = 1.0
    l = len(comment_similarity_array)
    for i1 in range(l):
        for i2 in range(i1 + 1, l):
            c1 = comment_similarity_array[i1]
            c2 = comment_similarity_array[i2]
            z *= compare_text(c1, c2)

    return z

def check_info(user):
    #print_comments(user)
    created = datetime.datetime.fromtimestamp(user.created_utc)
    created = created.strftime("%d/%m/%y")
    total_comments = 0
    comment_similarity_array = []
    links_array = []
    all_comments = user.comments.new(limit=None)

    # calculating n of links and n of commens
    for comments in all_comments:
        # print(f"links: {find_links(comments.body)}")
        # make a request to see if the link is shortened?
        # res code 3xx == shortened link
        # links_in_comments = find_links(comments.body)
        if total_comments < COMMENT_DEPTH and "://www." not in comments.body:
            comment_similarity_array.append(comments.body)
        total_comments += 1

    total_submissions = 0
    for submission in user.submissions.new(limit=None):
        total_submissions += 1

    data = [user.id,
            user.name,
            user.link_karma,
            user.comment_karma,
            user.total_karma,
            created,
            user.verified,
            total_submissions,
            total_comments]

    add_to_db(data)
    #print_account(data)
    account = Bot(data)


    # checks if user is found in bots.txt
    known = is_known_bot(user.name)

    if known:
        print(f"{cyan}{account.name}{green} has been found in the list.{reset}\n")

    account.print_bot()


    z = scan_comments(comment_similarity_array)
    if z > 0.3:
        print(f"1st Bot Detection Score: {red}{z} (Likely Bot){reset}")
    else:
        print(f"1st Bot Detection Score: {blue}{z} (Not Likely Bot){reset}")

    # -----------------------------
    #   Analysing account data
    # -----------------------------
    detect2_data = scanAccount(user.name, 50) # second detection algorithm

    if detect2_data > 129:
        print(f"""2nd Bot Detection Score: {red}{detect2_data} (Likely Bot){reset}""")
    else:
        print(f"""2nd Bot Detection Score: {blue}{detect2_data} (Not Likely Bot){reset}""")

    if ((detect2_data > 129 and z >= 0.3) or (detect2_data <= 129 and z < 0.3)):
        print(f"""{green}Agreement in Detection{reset}\n""")
    else:
        print(f"""{red}Disagreement in Detection{reset}\n""")

    if z >= 0.3 or detect2_data >= 130:
        print(f"Initiating further analysis")
        account.update_scores(z, detect2_data)
        account.set_user(user)
        further_analysis(account)
        current_scan.append(account)
        if len(account.reasons) > 0:
            print(f"{red}{account.reasons}{reset}")
    else:
        print(f"{green}{user.name} not found as a bot{reset}")


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

def is_declared_bot(bot):
    auto_declared = False
    if 'bot' in bot.name.lower():
        return True
    for comment in bot.user.comments.new(limit=5):
        if 'i am a bot' in comment.body.lower():
            auto_declared = True
    return auto_declared

def is_known_bot(username):
    with open('lists/bots.txt', 'r') as file:
        if any(username in line for line in file):
            return True # bot found in the list of bots
        else:
            return False

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

def is_shortened_link(url):
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return domain in SHORT_LINKS


def check_commentss(username):
    user = reddit.redditor(username)
    for comments in user.comments.new(limit=None):
        print(comments.body)
    print(f"checking comments for user {user.name}")
    z = 1.0
    seen = False
    for comments in user.comments.new(limit=5):
        print(comments.body)


def find_info(ids, depth):
    for i in ids:
        try:
        #if 1 == 1:
            submission = reddit.submission(id=i)
            print(f"Submission: {submission.url}")
            submission.comments.replace_more(limit=depth)
            for comment in submission.comments.list():
                if comment.author:
                    author = comment.author
                    user = reddit.redditor(author)
                    check_info(user)
        except RequestException:
            print("Request error occurred")
        except Exception as e:
            print(f"Exception {e} ocurred")

def options(reddit):
    count = 0
    try:
        x = input("1. Single search or 2. Submission search (1/2)? ")
        x = x.rstrip()
        if x == '1':
            x = input("Username or 0 to leave: ")
            #try:
            while x.rstrip() != '0':
                if '/u/' in x[0:3]:
                    x = x[3:]
                try:
                    count += 1
                    user = reddit.redditor(x)
                    check_info(user)
                except Exception as e:
                    print(f"{red}Error While finding user {blue}{x}{reset}\n{e}")
                x = input("Username or 0 to leave: ")
            print(f"{green}Finishing search.\n{yellow}Found {len(current_scan)} bots out of {count} accounts\n{reset}")
            for account in current_scan:
                print(f"{account.name=} {account.sim_score=} {account.lda_score=}")
                if len(account.reasons) > 0:
                    print(f"{red}{account.reasons=}{reset}")
                if account.good_bot:
                    print(f"{green}{account.name=}:{account.good_bot=}{reset}")
                option = ''
                options = []
                if decide(account, options):
                    print(f'To report this account:\n * follow the link->click on "..."->"Report Profile"->Username->reason->"Harmful Bots"')
                    option = input("1       - IGNORE ALL\n2       - IGNORE AUTODECLARED\n3       - IGNORE NON-CONCLUSIVE\n↵ Enter - Continue\n>")
                    option = option.rstrip()
                    if option == '1' and 'all' not in options:
                        options.append('all')
                    if option == '2' and 'good' not in options:
                        options.append('good')
                    if option == '3' and 'inconclusive' not in options:
                        options.append('inconclusive')
                    else:
                        continue


            print(f"Done deciding. {red}Exiting{reset}")
            exit()

        elif x == '2':
            subreddit = input("What subreddit you want to look at? ")
            z = input("New, Hot or top submissions? (N/H/T) ")
            y = int(input("How many posts to retrieve? "))

            posts =[]
            try:
                if z.lower() == 'n':
                    posts = reddit.subreddit(subreddit).new(limit=y)
                if z.lower() == 'h':
                    posts = reddit.subreddit(subreddit).hot(limit=y)
                if z.lower() == 't':
                    posts = reddit.subreddit(subreddit).top(limit=y)
                depth = int(input("Depth: "))
                post_ids = [post.id for post in posts]
                find_info(post_ids, depth)
            except Exception as e:
                print(f"{red}Error while fetching posts. Exiting.{reset}\n{e}")
                exit()
        else:
            print(f"No option {x} defined.\n\n")
            options(reddit)
    except KeyboardInterrupt:
            done = False
            print(f"{red}[+]ctrl + c detected\nExiting\n{yellow}found {len(current_scan)} possible bots out of {count} accounts\n{reset}")
            for account in current_scan:
                print(f"{account.name=}:{account.sim_score=}:{account.lda_score=}")
                if len(account.reasons) > 0:
                    print(f"{red}{account.name=}:{account.reasons=}{reset}")
                if account.good_bot:
                    print(f"{green}{account.name=}:{account.good_bot=}{reset}")
                done = decide(account, ['exiting'])
            if done:
                    print(f'To report account(s):\n * follow the link->click on "..."->"Report Profile"->Username->reason->"Harmful Bots"')
            print(f"Done deciding. {red}Exiting{reset}")



if __name__ == "__main__":
    # Initialize the Reddit API client
    reddit = praw.Reddit(client_id=client,
                         client_secret=key,
                         user_agent=user_agent)
    options(reddit)

