#!/usr/bin/python3

import gspread
import uuid
import json
import time
import pprint
import validators
from websocket import create_connection

# TODO: Make a default way of putting officials crews in a sheet and fill them in as well. 

team = {}
# These are the basic colours, right? Are there any others???
basiccolours = ["black", "white", "green", "red", "blue", "pink", "yellow", "purple", "gray", "grey", "orange", "brown"]
ws = create_connection("ws://localhost:8000/WS/")
gc = gspread.oauth(
            credentials_filename = "credentials.json"
        )


# This sends the message to the websocket. It only takes a k/v pair
def sendmessage( key, value):
    message = {
        "action": "Set",
        "key": key,
        "value": value,
        "flag": "" 
    }
    jmessage = json.dumps(message)
    ws.send(jmessage)

# This reads the team from a url and creates a prepared team in scoreboard
def create_team(url):
    teamuuid = str(uuid.uuid4())
    sh2 = gc.open_by_url(url)
    wks2 = sh2.worksheet("Charter Roster")
    try: 
        teamdata = wks2.col_values(3)
    except gspread.exceptions.APIError: 
        time.sleep(60)
        teamdata = wks2.col_values(3)


    leaguename = teamdata[3]
    teamname = teamdata[4]
    teamcolours = teamdata[5].casefold()
    colours = []
    for colour in basiccolours:
        if teamcolours.find(colour) >= 0:
            colours.append(colour)
    print("#####################################")
    print("League: " + leaguename)
    print("Team: " + teamname)
    print("Colours: " + ",".join(colours))
    team.update({
        teamuuid: {
            "FullName": leaguename + ": " + teamname,
            "LeagueName": leaguename,
            "Name": teamname,
            "Readonly": False,
            "TeamName": teamname,
            "skaters": {}
        }
    })
    sendmessage("ScoreBoard.PreparedTeam({uuid}).FullName".format(uuid=teamuuid), team[teamuuid]["FullName"])
    sendmessage("ScoreBoard.PreparedTeam({uuid}).Id".format(uuid=teamuuid), teamuuid)
    sendmessage("ScoreBoard.PreparedTeam({uuid}).LeagueName".format(uuid=teamuuid), team[teamuuid]["LeagueName"])
    sendmessage("ScoreBoard.PreparedTeam({uuid}).Name".format(uuid=teamuuid), team[teamuuid]["Name"])
    sendmessage("ScoreBoard.PreparedTeam({uuid}).TeamName".format(uuid=teamuuid), team[teamuuid]["Name"])
    sendmessage("ScoreBoard.PreparedTeam({uuid}).Readonly".format(uuid=teamuuid), False)
    for colour in colours:
        sendmessage("ScoreBoard.PreparedTeam({uuid}).UniformColor({c})".format(uuid=teamuuid, c=colour), colour)

    # Skaters start at row 13 and the last row will be row 32...
    # TODO: Would it be better to get the whole range, as that would only be 1 API call? 
    row = 13
    print("Skaters: ", end='')
    while row < 33:
        try:
            skater = wks2.row_values(row)
        except gspread.exceptions.APIError: 
            print("Going to sleep")
            time.sleep(60)
            skater = wks2.row_values(row)
        # unless there is no more skater, then break out the while loop
        if len(skater) == 1:
            break
        print(skater[1], end=' ', flush=True)
        skateruuid = str(uuid.uuid4())
        sendmessage("ScoreBoard.PreparedTeam({uuid}).Skater({suuid}).Name".format(uuid=teamuuid, suuid=skateruuid), skater[2])
        sendmessage("ScoreBoard.PreparedTeam({uuid}).Skater({suuid}).RosterNumber".format(uuid=teamuuid, suuid=skateruuid), skater[1])
        sendmessage("ScoreBoard.PreparedTeam({uuid}).Skater({suuid}).Id".format(uuid=teamuuid, suuid=skateruuid), skateruuid)
        sendmessage("ScoreBoard.PreparedTeam({uuid}).Skater({suuid}).Pronouns".format(uuid=teamuuid, suuid=skateruuid), skater[9])
        sendmessage("ScoreBoard.PreparedTeam({uuid}).Skater({suuid}).Flags".format(uuid=teamuuid, suuid=skateruuid), "")
        sendmessage("ScoreBoard.PreparedTeam({uuid}).Skater({suuid}).Readonly".format(uuid=teamuuid, suuid=skateruuid), False)
        row += 1
    print("")
    print("#####################################")
    return teamuuid

# This will create a game in scoreboard
def create_game(row):
    gamedata = wks.row_values(row)
    gsdate = gamedata[1]
    date = gsdate.split("/")[2] + "-" + "{:02d}".format(int(gsdate.split("/")[1])) + "-" + "{:02d}".format(int(gsdate.split("/")[0]))
    time = gamedata[2]
    teama = gamedata[3]
    teamauuid = team[teama]
    teamb = gamedata[5]
    teambuuid = team[teamb]
    game = gamedata[0] 
    print("#####################################")
    print("Game: " +game + " -- Date: " +date + " -- Time: " +time )
    print("Team A: " +teama + " -- Team B: " +teamb)
    print("#####################################")
    gameuuid = str(uuid.uuid4())
    gamename = "ScoreBoard.Game(" + str(gameuuid) +")"
    sendmessage("ScoreBoard.Game({uuid}).EventInfo(Date)".format(uuid=gameuuid), date)
    sendmessage("ScoreBoard.Game({uuid}).EventInfo(City)".format(uuid=gameuuid), city)
    sendmessage("ScoreBoard.Game({uuid}).EventInfo(HostLeague)".format(uuid=gameuuid), host)
    sendmessage("ScoreBoard.Game({uuid}).EventInfo(StartTime)".format(uuid=gameuuid), time)
    sendmessage("ScoreBoard.Game({uuid}).EventInfo(State)".format(uuid=gameuuid), country)
    sendmessage("ScoreBoard.Game({uuid}).EventInfo(Tournament)".format(uuid=gameuuid), tournament)
    sendmessage("ScoreBoard.Game({uuid}).EventInfo(Venue)".format(uuid=gameuuid), venue)
    sendmessage("ScoreBoard.Game({uuid}).EventInfo(GameNo)".format(uuid=gameuuid), game)
    sendmessage("ScoreBoard.Game({uuid}).Team(1).PreparedTeam".format(uuid=gameuuid), teamauuid)
    sendmessage("ScoreBoard.Game({uuid}).Team(2).PreparedTeam".format(uuid=gameuuid), teambuuid)


# TODO: This might be nicer in a def. 

print("Welcome to the tournament generator.")
print("Note 1: We need an up to date Tournament sheet")
print("Note 2: The links to charters need to be full URLS")
print("Enter sheet: (either a url or the key)")
sheet = input()
if validators.url(sheet):
    sh = gc.open_by_url(sheet)
else:
    sh = gc.open_by_key(sheet)

wks = sh.worksheet("Basic Info")

eventdata = wks.col_values(3)
tournament = eventdata[3]
host = eventdata[6]
venue = eventdata[13] 
city = eventdata[15]
country = eventdata[18]

print("====================================")
print("Tournament: " + tournament)
print("Host: " + host)
print("Location: " + venue + " " + city + " " + country)
print("====================================")

# Team info starts on row 34. If there are more than 16 teams, you need to do it yourself
row = 34
while row < 50:
    teaminfo = wks.row_values(row)
    if len(teaminfo) == 1:
        break
    name = teaminfo[1] 
    print("Doing team: " + name)
    teamurl = teaminfo[3]
    if not validators.url(teamurl):
        print("Charter URL for " + teaminfo[1] + " is not a url")
        exit(0)
    teamuuid = create_team(teaminfo[3])
    team.update({
        name : str(teamuuid)
    })
    row += 1

# The schedule, it starts on row 10 and there should not be more than 30 games.. If so, good luck! :) 
wks = sh.worksheet("Schedule")
row = 10
while row < 40:
    if not wks.get("B"+str(row))[0]:
        break
    create_game(row)
    row += 1
