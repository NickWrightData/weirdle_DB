#This script scan the Daily Weirdle reddit posts (on reddit.com/r/weirdle) for replies that share a
#   user's Weirdle score, and adds them to the postgresql DB on my machine.

import praw
from datetime import datetime
from postgres import postgres
import pprint as pp
import time
#Modified from a simplistic Reddit Bot script

#NOTE: Only the RedditBot account actions that are automated by this script will say they're 
#   automated.
userAgent = 'WeirdleBot'
cID = #[secret verification information]
cSC= #[secret verification information]
userN = 'WeirdleBot'
#userP = [The reddit bot password]
numFound = 0

reddit = praw.Reddit(user_agent=userAgent, client_id=cID, client_secret=cSC, username=userN,
                        password=userP, ratelimit_seconds=300)

#For use if I want to scan the entire subreddit for new posts or replies to non-Daily official posts
#subreddit = reddit.subreddit('weirdle')

weirdle_link_prefix = "https://old.reddit.com/r/weirdle/comments/"

#The 2 current weirdles (due to timezones; technically three, but only during an hour or two of the
#   day at like 2am)
#TODO: Automate this with a date or timestamp in the DB (table: weirdles); Ensure that the link ID
#   is added to the DB as well when I've set up automatically posting the Daily Weirdle post 
#   to reddit.
weirdle_a=31
weirdle_a_link="uwtzfa"
weirdle_a_post = reddit.submission(weirdle_a_link)

weirdle_b=32
weirdle_b_link="uxl80l"
weirdle_b_post = reddit.submission(weirdle_b_link)

#Evaluate the comment and determine how many tries it took to guess the song--6 is the max, 7 means
#   it would have taken 7 or more tries, which is a loss
def get_tries(comment):
    #White = guessed correctly before this guess (if guessed correctly on try #4, #5 & #6 will be white/blank
    #green = correct guess
    #black = skipped
    #red = incorrect guess
    #accordion = accordion emoji
    #cross_out = Circle with a line through it to imply a loss
    white_box = "⬜️"
    green_box = "🟩"
    black_box = "⬛️"
    red_box = "🟥"
    accordion ="🪗"
    cross_out = "🚫"
    #The cross_out should not appear with a green box, but I do this for the rare case the user 
    #  adds their own crossout emoji in a comment; hasn't happened to my knowledge
    if cross_out in comment.body and green_box not in comment.body:
        return 7
    else:
        #
        return comment.body.count(black_box) + comment.body.count(red_box) + 1

#A Bracket is the set of users who have completed the same number of Weirdles; this does NOT mean
#   they have to have completed the same SET of Weirdles!
#This method evaluates a user's place within a bracket; if in a bracket of 20 people, five users
#   have a perfect score of 1, then all five of them are in the "top 5 of 20."
def place(bracket_stats, author_id):
    placement = 1
    #The bracket_stats are already ordered
    for entry in bracket_stats:
        if int(entry[0]) is not int(author_id):
            placement += 1
        else:
            return str(placement)
            
#Evaluates a user's game history to determine their current and record streaks, 
#   for both flawless (1 guess) and any win (up to 6 guesses needed)
def streaks(streak_stats):
    r_f_streak = 0      #record flawless streak
    c_f_streak = 0      #current flawless streak
    r_w_streak = 0      #record win streak
    c_w_streak = 0      #current win streak
    last_weirdle = 0
    for stat in streak_stats:
        weirdle_number = stat[1]
        tries = stat[2]
        
        c_f_streak += 1
        c_w_streak += 1
        
        if weirdle_number - 1 > last_weirdle:
            c_f_streak = 1
            c_w_streak = 1
        
        if tries == 7:
            c_f_streak = 0
            c_w_streak = 0
        elif tries > 1:
            c_f_streak = 0
            
        if c_f_streak > r_f_streak:
            r_f_streak = c_f_streak
        
        if c_w_streak > r_w_streak:
            r_w_streak = c_w_streak
            
        last_weirdle = weirdle_number
        
    return [str(r_f_streak),str(c_f_streak),str(r_w_streak),str(c_w_streak)]
    
#This method, when given a comment ID and the weirdle number in it, will reply to a user on Reddit
#   with their running streaks (see streaks()).
def log_and_send_reply(comment, weirdle_number):
    #print(comment.body)
    tries = get_tries(comment)
    
    if postgres.new_weirdler(comment.author):
        author_id = postgres.addWeirdleUser(comment.author)
    else:
        author_id = str(postgres.getWeirdlerID(comment.author))
    
    #print(author_id)
    #print(tries)
    #print(weirdle_number)
    postgres.addWeirdleSubmission(author_id, tries, weirdle_number)
    author_string = str(comment.author)
    attempt_count = str(postgres.getWeirdleCountUser(author_id))
    percent = str(round(float(attempt_count)/float(weirdle_number)*100,2))
    average = str(round(postgres.getWeirdleAverageUser(author_id),2))
    bracket_stats = postgres.getWeirdleAveragesAtBracket(author_id,attempt_count)
    #pprint.pprint(bracket_stats)
    placement = place(bracket_stats,author_id)
    [r_f_streak, c_f_streak, r_w_streak, c_w_streak] = streaks(postgres.getStreaks(author_id))
    
    return_phrase = ''\
    '    PLAYER: u/'+author_string+'\n'\
    '\n'\
    '    TOTAL WEIRDLES COMPLETED: '+attempt_count+' ('+percent+'% OF '+weirdle_number+' WEIRDLES)\n'\
    '    AVERAGE WEIRDLE SCORE: '+average+' (TOP '+placement+' OF '+str(len(bracket_stats))+' IN ABOVE BRACKET)\n'\
    '\n'\
    '    RECORD FLAWLESS STREAK: '+r_f_streak+'\n'\
    '    CURRENT FLAWLESS STREAK: '+c_f_streak+'\n'\
    '\n'\
    '    RECORD WIN STREAK: '+r_w_streak+'\n'\
    '    CURRENT WIN STREAK: '+c_w_streak+'\n'\
    '\n'\
    '    (THIS ACTION WAS PERFORMED AUTOMATICALLY.\n'\
    '    PLEASE MESSAGE u/NickWrightData OR REPLY TO ME\n'\
    '    IF ANYTHING SEEMS WRONG!)'
    print(return_phrase)
    comment.reply(body=return_phrase)

#MAIN LOOP
#This loop is where the script scans the two above reddit posts for any self-reported scores
#   In the future, this or another loop may scan the entire subreddit's top posts for self-repots
#   and/or may search for people requesting their (or others') score totals and stats directly from
#   querying the bot without having to submit a score at the time.
#   ex: "u/WeirdleBot What's my score?" -- would check if the phrase "whats my score" existed in the
#   reddit reply, if all punctuation is removed and all letters were lowercased

print("Searching in Reddit posts for Weirdles "+str(weirdle_a)+" & "+str(weirdle_b)+"...")
while 1:
    weirdle_a_post = reddit.submission(weirdle_a_link)
    weirdle_b_post = reddit.submission(weirdle_b_link)
    for submission in [weirdle_a_post, weirdle_b_post]:
        #Check to see if any comments on these posts are #Weirdle submission posts
        for comment in submission.comments:
            if "#Weirdle #" in comment.body:
                #WEIRDLE SUBMISSION! Check to see if I've already replied (automatically or not)
                replied = False
                for reply in comment.replies:
                    #print(reply.body)
                    if "PLAYER:" in reply.body:
                        #I already replied, do nothing
                        #print("already replied")
                        replied = True
                if not replied:
                    #REPLY! *IF* it's in the right thread!
                    bodyArray = comment.body.split()
                    if "#Weirdle" in bodyArray:
                        post_weirdle_number = bodyArray[bodyArray.index("#Weirdle")+1]
                    elif "\#Weirdle" in bodyArray:
                        post_weirdle_number = bodyArray[bodyArray.index("\#Weirdle")+1]
                    else:
                        print("Neither '#Weirdle' nor '\#Weirdle' are in the comment! Investigate!")
                        exit(0)
                    #Test if the weirdle number in the reply is the same as the one in the post title
                    if post_weirdle_number in submission.title:
                        #print(submission.title)
                        #print(comment.body)
                        print("Replying...")
                        log_and_send_reply(comment,post_weirdle_number[1:])
                        print(submission.url+str(comment))
                    else:
                        #Reply with "This isn't the place to post this!"
                        pass
    time.sleep(30)