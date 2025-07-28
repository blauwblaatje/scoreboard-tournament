# scoreboard-tournament
Create games in Roller Derby Scoreboard from Sanctioning docs

This is just a start, but pull requests are welcome.


# How it works
- Get Google API credentials in credentials.json
- They need to be able to read google docs. TODO: how-to :)
- You need to install some python libs:
  * gspread
  * validators
  (this should probably go into a Requirements...)
- Have Scoreboard running
- On linux run: ./tournament.py 
- Enter either a full URL of a sanctioning sheet or only the key
- ???
- Profit..  Well, at least you get all the games in Scoreboard


After this you should be able to get the paperwork out of it.


# Todos
- Probably a refactor, as I'm a shitty programmer :P
- Make a Requirements file :)
- Get all the skaters in a roster with one API call, that should speed it up

# Extra feature: Officials
It would be nice to also input the officials. Although there's no std way to do that.. For myself I can at least make a default sheet.
Sheet should link position, name and OHD, so info about affiliation and Cert level can come from OHD. (uhhhhm, that can be tricky)
Also two options:
- Create a crew and note which crew does what
- Create a list per game
I think most of the time it'll be the first with small changes that you always need to make. 
