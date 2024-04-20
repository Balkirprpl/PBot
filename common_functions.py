from keys import key, client, user_agent
import praw


reddit = praw.Reddit(
    client_id = client,
    client_secret = key,
    user_agent = user_agent
)
