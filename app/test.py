import praw
reddit = praw.Reddit(client_id='VcSCegzGWO8Frg',
                     client_secret='1IVb5rrY7YbfDJVhkq2jRWabvCU',
                     user_agent='prawuseragent',
                     username='ece1779agent',
                     password='Yan8318161')
for submission in reddit.subreddit('popular').hot(limit=1):
    print(submission.title)
    submission.comments.replace_more(limit=0)
    for top_level_comment in submission.comments:
        print(top_level_comment.body)
        break