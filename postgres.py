#This python class is to separate concerns; all postgres-accessing code goes here.
#   This includes all text for calls to the database.
#I'm planning on replacing the word "weirdler" with "user" throughout this code and the database,
#   as "weirdler" is a little confusing and a little hard to spell.
#TO DO: GET RID OF camelCase!

import psycopg2            #for connecting to DB
from psycopg2 import sql

class postgres:
    #The generalized "run any query" function
    def runQuery(query, values=[], get_results=True):
        database = "weirdle"
        user = "postgres"
        password = "pokemonbot"

        try:
            conn=psycopg2.connect("dbname="+database+" user="+user+" password="+password)
        except:
            print("DB connection unsuccessful.")
            exit(0)

        cur = conn.cursor();
        
        returned_val = cur.execute(sql.SQL(query),[i for i in values]);
        
        conn.commit()
        
        #Change to "if insert" (and reverse)?
        if get_results:
            #If it's a query, i.e. multiple results
            return cur.fetchall()
        else:
            #If it's an insert and we want the id
            return returned_val
    
    #The remaining functions will be for specific queries, each including their 
    
    #Whether or not a user exists in the database under that site's (reddit or otherwise) username
    #(rename to is_new_weirdler?)
    def new_weirdler(author):
        return not postgres.runQuery("""SELECT weirdlers.weirdler_id
                FROM weirdlers
                WHERE weirdlers.reddit_un = %s""",[str(author)])
        
    #This method gets the Weirdler ID from the username
    #As people have different usernames on different accounts, we won't necessarily be able to tell
    #   if a user is represented via multiple rows, however usually people submit their scores once
    #   so this probably shouldn't be an issue.
    #Which social column to check the username for is determined by the boolean passed in.
    def getWeirdlerID(author, twitter=False, facebook=False, mastodon=False, tiktok=False):
        if twitter:
            site="twitter";
        elif facebook:
            site="facebook";
        elif mastodon:
            site="mastodon";
        elif tiktok:
            site="tiktok";
        else:
            site="reddit";
        returnable= postgres.runQuery("""SELECT weirdlers.weirdler_id
                FROM weirdlers
                WHERE lower(weirdlers."""+site+"""_un) = %s""",[str(author).lower()])
        #print(returnable)
        if returnable:
            return returnable[0][0]
        else:
            pass
    
    #Select all weirdler (user) IDs 
    def getUsers():
        return postgres.runQuery("""SELECT weirdler_id
                FROM weirdlers
                ORDER BY weirdler_id""")
    
    #Get the user's account name (once again, depending on the provided social media)
    def getUser(userID, twitter=False, facebook=False, mastodon=False, tiktok=False):
        if twitter:
            site="twitter";
        elif facebook:
            site="facebook";
        elif mastodon:
            site="mastodon";
        elif tiktok:
            site="tiktok";
        else:
            site="reddit";
        return postgres.runQuery("""SELECT """+site+"""_un
                FROM weirdlers
                WHERE weirdler_id = %s""", [str(userID)])[0][0]
    
    #Get the count of Weirdles completed by a specific user
    def getWeirdleCountUser(author):
        return postgres.runQuery("""SELECT COUNT(*)
                FROM user_scores
                WHERE user_scores.user_id = %s""",[str(author)])[0][0]
                    
    #Get the count of users that completed a specific Weirdle
    def getWeirdleTotal(weirdle_id):
        return postgres.runQuery("""SELECT COUNT(*)
                FROM user_scores
                WHERE user_scores.weirdle_id = %s""",[str(weirdle_id)])[0][0]
    
    #Get the average of submitted scores for a specific User
    def getWeirdleAverageUser(author):
        return postgres.runQuery("""SELECT AVG(tries)
                FROM user_scores
                WHERE user_scores.user_id = %s""",[str(author)])[0][0]
                
    #Get the average of submitted scores for a specific Weirdle
    def getWeirdleAverage(weirdle_id):
        return postgres.runQuery("""SELECT AVG(tries)
                FROM user_scores
                WHERE user_scores.weirdle_id = %s""",[str(weirdle_id)])[0][0]
        
    #Get the list of users and each of their average, and total numer of, results, for bracket
    #   purposes.
    def getWeirdleAveragesAtBracket(author,count):
        return postgres.runQuery("""SELECT user_scores.user_id, AVG(tries), COUNT(tries)
                FROM user_scores
                GROUP BY user_scores.user_id
                HAVING COUNT(tries) = %s
                ORDER BY AVG(tries), user_scores.user_id ASC""",[str(count)])
    
    #
    def getStreaks(author):
        return postgres.runQuery("""SELECT user_id, weirdle_id, tries
                FROM user_scores
                WHERE user_id = %s""",[str(author)])
                
    #Adds a new weirdler/user, returning the new ID
    def addWeirdleUser(author, twitter=False, facebook=False, mastodon=False, tiktok=False):
        if twitter:
            site="twitter";
        elif facebook:
            site="facebook";
        elif mastodon:
            site="mastodon";
        elif tiktok:
            site="tiktok";
        else:
            site="reddit";
        #We've determined we need to add a user first. Let's do it.
        author_result = postgres.runQuery("""INSERT INTO weirdlers ("""+site+"""_un)
                VALUES (%s) RETURNING weirdler_id""",[str(author)])
                
        author_id = author_result[0][0]
        print(str(author) + " added to database. ID: "+str(author_id))
            
        return author_id
    
    #Adds a new self-submitted weirdle score
    def addWeirdleSubmission(author, tries, weirdle_number):
        #Check that this has not already been submitted!
        already_submitted = postgres.runQuery("""SELECT COUNT(*)
                FROM user_scores
                WHERE user_scores.user_id = %s AND user_scores.weirdle_id = %s""",[str(author), str(weirdle_number)])[0][0]
                
        if not already_submitted:
            postgres.runQuery("""INSERT INTO user_scores (user_id, weirdle_id, tries) VALUES 
            (%s, %s, %s)""",[author, weirdle_number, tries], False)
            print("User ID #" + str(author) + " scoring " + str(tries) + " on Weirdle #" 
                + str(weirdle_number) + " added to database.")
            return True
        else:
            print("You have already submitted this user's score for this weirdle;\n\
                    Changing it requires modifying, not adding, a weirdle.")
            return False
            
        return author
