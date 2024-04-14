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



