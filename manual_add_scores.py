#This script is to be run when saving results from sites other than reddit (facebook, twitter, etc)
#   It is a step-by-step process that allows for much more intuitive and flexible addition of data
#   to the database.
#FUTURE PLANS: Automate this? I can automate on Twitter, what about facebook? Might not be possible
from postgres import postgres

#This is the exact same as the streaks() function in reddit_bot.py.
#FUTURE PLANS: put all THREE of these copies of this function in a single, shared file!
def streaks(streak_stats):
    #pp.pprint(streak_stats)
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
        
#This is the exact same as the place() function in reddit_bot.py.
#FUTURE PLANS: put both copies of this function in a single, shared file!
def place(bracket_stats, author_id):
    placement = 1
    for entry in bracket_stats:
        if int(entry[0]) is not int(author_id):
            placement += 1
        else:
            return str(placement)

#For generating reply text similar to the text generated in reddit_bot.py
#FUTURE PLANS: Again, put this and the code in reddit_bot.py in the same file to elimiate
#   code duplication.
def reply_text(weirdle_number, user_id, username):
    #author_string = postgres.getUser(user_id)
    attempt_count = str(postgres.getWeirdleCountUser(user_id))
    percent = str(round(float(attempt_count)/float(weirdle_number)*100,2))
    average = str(round(postgres.getWeirdleAverageUser(user_id),2))
    bracket_stats = postgres.getWeirdleAveragesAtBracket(user_id,attempt_count)
    placement = place(bracket_stats,user_id)
    [r_f_streak, c_f_streak, r_w_streak, c_w_streak] = streaks(postgres.getStreaks(user_id))
    
    return_phrase = ''\
    '    PLAYER: u/'+username+'\n'\
    '\n'\
    '    TOTAL WEIRDLES COMPLETED: '+attempt_count+' ('+percent+'% OF '+str(weirdle_number)+' WEIRDLES)\n'\
    '    AVERAGE WEIRDLE SCORE: '+average+' (TOP '+placement+' OF '+str(len(bracket_stats))+' IN ABOVE BRACKET)\n'\
    '\n'\
    '    RECORD FLAWLESS STREAK: '+r_f_streak+'\n'\
    '    CURRENT FLAWLESS STREAK: '+c_f_streak+'\n'\
    '\n'\
    '    RECORD WIN STREAK: '+r_w_streak+'\n'\
    '    CURRENT WIN STREAK: '+c_w_streak+'\n'\
    '\n'\
    '    (PLEASE MESSAGE u/NickWrightData OR REPLY TO ME\n'\
    '    IF ANYTHING SEEMS WRONG!)'
    
    return return_phrase;

#The main loop--looped to facilitate ease of adding several people all right after each other.
while(1):
    username = ""
    site = ""
    prefix = "username? u/"
    while (not site.isdigit() or int(site) < 0 or int(site) > 4):
        site = input("What is the site? 0=reddit, 1=twitter, 2=facebook, 3=mastodon.social, 4=tiktok: ")
    site = int(site)
    if site == 1:
        prefix = "username? @"
    elif site == 2:
        prefix = "name? "
    elif site == 3:
        prefix = "username? @@"
    elif site == 4:
        prefix = "username? "
    
    weirdle_number = -1
    
    while (username == ""):
        username = input("What is the "+prefix)
    
    if site == 1:
        user_id = postgres.getWeirdlerID(username, twitter=True)
    elif site == 2:
        user_id = postgres.getWeirdlerID(username, facebook=True)
    elif site == 3:
        user_id = postgres.getWeirdlerID(username, mastodon=True)
    elif site == 4:
        user_id = postgres.getWeirdlerID(username, tiktok=True)
    elif site == 0:
        user_id = postgres.getWeirdlerID(username)
    
    if not user_id and input("New user? (y/n) ") == 'y':
        if site == 1:
            user_id = postgres.addWeirdleUser(username, twitter=True)
        elif site == 2:
            user_id = postgres.addWeirdleUser(username, facebook=True)
        elif site == 3:
            user_id = postgres.addWeirdleUser(username, mastodon=True)
        elif site == 4:
            user_id = postgres.addWeirdleUser(username, tiktok=True)
        elif site == 0:
            user_id = postgres.addWeirdleUser(username)
    elif not user_id:
        print("ERROR: User does not exist.")
        exit(0)
    
    if input("ID: " + str(user_id)+". Insert score for this user? (y/n) ").lower() == 'y':
        curr_weird = 31
        weirdle_number = 0
        while (weirdle_number == 0):
            weirdle_number = input("("+str(curr_weird)+") Weirdle #") or curr_weird

        tries = input("# of tries it took? 1=perfect, 6=max, 7=lost: ")
        if input("Add User #" + str(user_id) + " scoring " + str(tries) + " on Weirdle #" 
                + str(weirdle_number) + " to database? (y/n) ") == 'y':
            if postgres.addWeirdleSubmission(user_id, tries, weirdle_number):
                #Result actually submitted
                print()
                print(reply_text(weirdle_number, user_id, username))
            print()