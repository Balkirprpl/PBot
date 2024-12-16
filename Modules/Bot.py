from Modules.colors import cyan, blue, yellow, red, green, reset

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
""")

