from postgres import postgres

#This script gives a summary of a Weirdle's statistics. It's meant to be run at the end of the
#   Weirdle's day--for any person in any time zone (which means >48 hours after it is first
#   available for the first time zones.) The output is to be used to update the daily Weirdle
#   posts on reddit, once the Weirdle is over for everyone.
#Future plans: use this in an automation for the daily posts on reddit, as well as de-commissioning
#   the older posts as their daily weirdles are no longer available to play.

#streaks() and work very similarly to the one in reddit_bot.py, however the key difference is that
#   this one requires a "max_weirdle_number"--since that number is already assumed to be the one
#   that a user will submit. This number is the weirdle number we need to stop at in order to give
#   an accurate streaks result for this Weirdle.
#Future plans: Put this in a shared file, so that the code isn't duplicated!
def streaks(streak_stats, max_weirdle_number):
    #pp.pprint(streak_stats)
    r_f_streak = 0      #record flawless streak
    c_f_streak = 0      #current flawless streak
    r_w_streak = 0      #record win streak
    c_w_streak = 0      #current win streak
    last_weirdle = 0
    for stat in streak_stats:
        weirdle_number = stat[1]
        if (weirdle_number <= max_weirdle_number):
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
    
weirdle_number = input("What weirdle are we wrapping up? #")
users = postgres.getUsers()
total_weirdle_count = postgres.getWeirdleTotal(weirdle_number)
average_weirdle_score = postgres.getWeirdleAverage(weirdle_number)

#r = record, c = current, f = flawless, w = wins (any)
best_c_f = 0
best_c_f_users = []
best_r_f = 0
best_r_f_users = []
best_c_w = 0
best_c_w_users = []
best_r_w = 0
best_r_w_users = []



#TO DO: COUNT OF USERS:
#SELECT count(*) FROM user_scores WHERE weirdle_id = 28;

#MAKE SURE TO round() THIS:
#TO DO: AVERAGE OF SUBMISSIONS:
#SELECT avg(tries) FROM user_scores WHERE weirdle_id = 28;

#Determining which users, and how many, are in each category--record flawless, current flawless, 
#   record wins, and current wins. Along with their respective streak counts.
for (user, ) in users:
    r_f_streak, c_f_streak, r_w_streak, c_w_streak = streaks(postgres.getStreaks(user),int(weirdle_number))
    r_f_streak, c_f_streak, r_w_streak, c_w_streak = int(r_f_streak), int(c_f_streak), int(r_w_streak), int(c_w_streak)
        
    if (best_r_f < r_f_streak):
        best_r_f = r_f_streak
        best_r_f_users = [user]
    elif (best_r_f == r_f_streak):
        best_r_f_users.append(user)
        
    if (best_c_f < c_f_streak):
        best_c_f = c_f_streak
        best_c_f_users = [user]
    elif (best_c_f == c_f_streak):
        best_c_f_users.append(user)
        
    if (best_r_w < r_w_streak):
        best_r_w = r_w_streak
        best_r_w_users = [user]
    elif (best_r_w == r_w_streak):
        best_r_w_users.append(user)
        
    if (best_c_w < c_w_streak):
        best_c_w = c_w_streak
        best_c_w_users = [user]
    elif (best_c_w == c_w_streak):
        best_c_w_users.append(user)

print(total_weirdle_count)
print(average_weirdle_score)
print (best_r_w)
print (best_r_w_users)
print (best_c_w)
print (best_c_w_users)
print (best_r_f)
print (best_r_f_users)
print (best_c_f)
print (best_c_f_users)