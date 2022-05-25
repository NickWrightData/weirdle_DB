# weirdle_DB
Code for interacting with http://weirdle.app's database and for the reddit bot--the databse is either updated through the reddit api bot or manually updated (via a script here) for twitter, facebook, etc.

To understand this code, you will first need to understand weirdle.app.

This all starts with Wordle (now owned by the NYT: https://www.nytimes.com/games/wordle/index.html), a puzzle game you can only play once a day, where you have six tries to guess the five-letter word. It's pretty simple, and everyone gets the same word each day, which increases the appeal and shareability of your scores.

After Wordle came http://heardle.app, a similar online game where you try to guess the song in the first few seconds of its intro. Like with Weirdle, you play the same song as everyone else playing that day.

Heardle now has tons of variations for every game OST, artist, or genre you can imagine. If the one you're imagining doesn't exist yet, you can go make it with open-source code online with glitch.me!

In any case, I took this code and crafted a "Weird Al" Yankvic version of Heardle called Weirdle, which can be found at http://weirdle.app. Every day is a new song of his you have to guess from only listening to the first few seconds of its intro.

THAT code is not here; this is separate code I created for a reddit bot and postgres DB to import the scores people share online to one place, in order to analyze them.
In the future, I may create more bots for crawling separate sites (like twitter), or create functionality for users on reddit to interact with the bot.

Several different scripts I've created here facilitate the ability to manually read results online and quickly and efficiently input them into the database. I also have a script that summarizes a Weirdle's scores after the Weirdle is done, for posting to the reddit page--subreddit.

The ultimate goal would be to host weirlde.app from my own machine, so that when anyone completes a weirdle, I can add their completed score (anonymously, as I won't have any user data to match it to) to my database. Many more people complete such wordles/heardles/weirdles than those who share them.

Sites:
http://weirdle.app
glitch.com/edit/#!/weirdle (weirdle.app code--in Javascript as well as Klingon--I kid, as well as css.
reddit.com/r/weirdle

bot:
reddit.com/u/WeirdleBot
