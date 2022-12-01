import discord
import json
import requests
from discord.ext import commands
from discord import app_commands

bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())

#This array contains all player data
registeredPlayers = []

#Global Boolean for whether the Audit log is toggled on or off (Currently the Audit Log does not work)
audit = False

#Keeping track of map names and the amount of times they've been played
alley = "Alleyway"
alleyInt = 0
atom = "Atomic"
atomInt = 0
mirage = "Mirage"
mirageInt = 0
carrier = "Carrier"
carrierInt = 0
cobble = "Cobblestone"
cobbleInt = 0
train = "Train"
trainInt = 0
op = "Overpass"
opInt = 0
og = "Overgrown"
ogInt = 0
cache = "Cache"
cacheInt = 0
ancient = "Ancient"
ancientInt = 0
sand = "Sandstorm"
sandInt = 0
temple = "Temple"
templeInt = 0

#My own API key so I can access the API easily
API_KEY = "deb9e086-d418-42f8-9de5-03676d1f98d9"

#The Player object stores an individuals statistics for Ranked CvC
class Player(object):
    def __init__(self, name, kills, deaths, kdr, wins, losses, rank, rating, gp, wlr, rp, kpr):
        self.name = name
        self.kills = kills
        self.deaths = deaths
        self.kdr = kdr
        self.wins = wins
        self.losses = losses
        self.rank = rank
        self.rating = rating
        self.gp = gp
        self.wlr = wlr
        self.rp = rp
        self.kpr = kpr

    def __repr__(self):
        return repr((self.name, self.kills, self.deaths, self.kdr, self.wins, self.losses, self.rank, self.rating,
                     self.gp, self.wlr, self.rp, self.kpr))

#I'm not sure why I made this I don't think I use it
def find(list, name):
    for x in list:
        if name == x:
            return x.index

#Grabs the UUID of a registered user
def get_uuid(player):
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{player}")
    try:
        uuid = json.loads(response.text)['id']
        return uuid
    except:
        return 'ERROR'

#Prepares to make a call to the API
def getinfo(call):
    r = requests.get(call)
    return r.json()

#Returns all of a player's data from the API
def get_API(player):
    data = getinfo(f"https://api.hypixel.net/player?key={API_KEY}&uuid={player}")
    return data

@bot.event
async def on_ready():
    activity = discord.Game(name="Cozy Ranked!")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print('We have logged in as {0.user}'.format(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

#Error Handling
@bot.tree.error
async def on_application_command_error(interaction, error):
    #If the user generates the error that they were missing the required role for a command
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("You do not have the specific role to run this command", ephemeral=True)
    else:
        raise error

@bot.tree.command(name="help", description="Check out the commands you can use")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message("Help: Displays the command you are currently using\n"
                                             "r (username): Check a player's stats\n"
                                             "register (username): Register a player for Ranked CvC\n"
                                             "lb: Check the first page of the Ranked CvC Leaderboards\n"
                                             "lb2: Check the second page of the Ranked CvC Leaderboards\n"
                                             "lb3: Check the third page of the Ranked CvC Leaderboards\n"
                                             "Captains (10 usernames): Input 10 usernames to determine the captains of a Ranked CvC game\n"
                                             "maps: Check how often certain maps are played in Ranked CvC\n"
                                             "top10(wins/deaths/kills/losses/kdr/kpr/gp/rp/wlr): Check the top 10 of different statistical categories for Ranked CvC", ephemeral=True)

#Command to check a player's stats
#Param: Takes a string as a username
@bot.tree.command(name="r", description="Check a player's stats")
@app_commands.describe(username="Check a users stats")
async def r(interaction: discord.Interaction, username: str):
    global registeredPlayers
    player = username
    #Set default values for k/d and w/l so we don't divide by 0
    kd = 0
    wl = 0
    true = 0
    kpr = 0

    #Iterate through our list of players to find the right one
    for x in registeredPlayers:
        if player.lower() == x.name.lower():
            #Set our flag so we know we found the player
            true = 1
            if x.deaths != 0:
                kd = round((x.kills / x.deaths), 3)
            if x.gp != 0:
                wl = round((x.wins / x.gp) * 100, 3)
            elif x.losses == 0 and x.wins > 0:
                wl = 100
            if x.rp != 0:
                kpr = round(x.kills / x.rp, 3)
            await interaction.response.send_message(
                f"{x.name} has rank {x.rank} with a rating of {x.rating} with a KDA of {kd}"
                f", a W/L of {x.wins}/{x.losses} ({wl}%), and a KPR of {kpr}")
    if true == 0:
        await interaction.response.send_message("Invalid Player")

#Command to register a user for Ranked CvC
#Param: Takes a username as a string
@bot.tree.command(name="cvcregister", description="Register a player")
@app_commands.describe(username="Register a player")
async def cvcregister(interaction: discord.Interaction, username: str):
    global registeredPlayers
    player = username
    #Grab the UUID
    uuid = get_uuid(player)
    #Set a variable as a flag for if the user is already registered
    dupe = -2

    #If the UUID is valid
    if uuid != "ERROR":
        #Grab the player's API
        stats = get_API(uuid)
        try:
            #If the user has generated the API endpoint for winning a game of defusal, then return the wins they have
            cvc_defusal_wins = stats["player"]["stats"]["MCGO"]["game_wins"]
        except:
            #Otherwise, set their wins to 0
            cvc_defusal_wins = 0

        if cvc_defusal_wins == 0:
            #If they don't have enough wins they can't register
            await interaction.response.send_message("Invalid Player")
            return

        for x in registeredPlayers:
            #By this point we've established they have enough wins to player, check if they are already registered
            if player.lower() == x.name.lower():
                #If we find them, set the flag to true
                dupe = 1

        if dupe != 1:
            #If the flag is not true (meaning there are no duplicates), create a Player object with default stats
            app = Player(player, 0, 0, 0, 0, 0, len(registeredPlayers) + 1, 1500, 0, 0, 0, 0)
            #Append them to the player list
            registeredPlayers.append(app)
            await interaction.response.send_message(f"{player} has been registered")
        else:
            await interaction.response.send_message(f"{player} was already registered")

        #Sort the list of player's by rating from highest to lowest
        registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
        #Update their rank by going through the list starting at 0 and assigning them the rank index+1
        for i in range(len(registeredPlayers)):
            registeredPlayers[i].rank = i + 1
    else:
        #If the UUID wasn't valid then the account doesn't exist
        await interaction.response.send_message("Invalid Player")


@bot.tree.command(name="lb", description="Displays the first page of the Leaderboard")
async def lb(interaction: discord.Interaction):
    global registeredPlayers
    #I know this code is ugly, but if I loop the messages it does 1 message at a time and takes awhile
    #It may be ugly but it's a lot more efficient
    #Maybe there is some way to yield until I'm done looping but I never looked into that
    try:
        await interaction.response.send_message(f"```1. {registeredPlayers[0].name} - {registeredPlayers[0].rating}\n"
                                                f"2. {registeredPlayers[1].name} - {registeredPlayers[1].rating}\n"
                                                f"3. {registeredPlayers[2].name} - {registeredPlayers[2].rating}\n"
                                                f"4. {registeredPlayers[3].name} - {registeredPlayers[3].rating}\n"
                                                f"5. {registeredPlayers[4].name} - {registeredPlayers[4].rating}\n"
                                                f"6. {registeredPlayers[5].name} - {registeredPlayers[5].rating}\n"
                                                f"7. {registeredPlayers[6].name} - {registeredPlayers[6].rating}\n"
                                                f"8. {registeredPlayers[7].name} - {registeredPlayers[7].rating}\n"
                                                f"9. {registeredPlayers[8].name} - {registeredPlayers[8].rating}\n"
                                                f"10. {registeredPlayers[9].name} - {registeredPlayers[9].rating}\n"
                                                f"11. {registeredPlayers[10].name} - {registeredPlayers[10].rating}\n"
                                                f"12. {registeredPlayers[11].name} - {registeredPlayers[11].rating}\n"
                                                f"13. {registeredPlayers[12].name} - {registeredPlayers[12].rating}\n"
                                                f"14. {registeredPlayers[13].name} - {registeredPlayers[13].rating}\n"
                                                f"15. {registeredPlayers[14].name} - {registeredPlayers[14].rating}\n"
                                                f"16. {registeredPlayers[15].name} - {registeredPlayers[15].rating}\n"
                                                f"17. {registeredPlayers[16].name} - {registeredPlayers[16].rating}\n"
                                                f"18. {registeredPlayers[17].name} - {registeredPlayers[17].rating}\n"
                                                f"19. {registeredPlayers[18].name} - {registeredPlayers[18].rating}\n"
                                                f"20. {registeredPlayers[19].name} - {registeredPlayers[19].rating}\n"
                                                f"21. {registeredPlayers[20].name} - {registeredPlayers[20].rating}\n"
                                                f"22. {registeredPlayers[21].name} - {registeredPlayers[21].rating}\n"
                                                f"23. {registeredPlayers[22].name} - {registeredPlayers[22].rating}\n"
                                                f"24. {registeredPlayers[23].name} - {registeredPlayers[23].rating}\n"
                                                f"25. {registeredPlayers[24].name} - {registeredPlayers[24].rating}\n"
                                                f"26. {registeredPlayers[25].name} - {registeredPlayers[25].rating}\n"
                                                f"27. {registeredPlayers[26].name} - {registeredPlayers[26].rating}\n"
                                                f"28. {registeredPlayers[27].name} - {registeredPlayers[27].rating}\n"
                                                f"29. {registeredPlayers[28].name} - {registeredPlayers[28].rating}\n"
                                                f"30. {registeredPlayers[29].name} - {registeredPlayers[29].rating}\n"
                                                f"31. {registeredPlayers[30].name} - {registeredPlayers[30].rating}\n"
                                                f"32. {registeredPlayers[31].name} - {registeredPlayers[31].rating}\n"
                                                f"33. {registeredPlayers[32].name} - {registeredPlayers[32].rating}\n"
                                                f"34. {registeredPlayers[33].name} - {registeredPlayers[33].rating}\n"
                                                f"35. {registeredPlayers[34].name} - {registeredPlayers[34].rating}\n"
                                                f"36. {registeredPlayers[35].name} - {registeredPlayers[35].rating}\n"
                                                f"37. {registeredPlayers[36].name} - {registeredPlayers[36].rating}\n"
                                                f"38. {registeredPlayers[37].name} - {registeredPlayers[37].rating}\n"
                                                f"39. {registeredPlayers[38].name} - {registeredPlayers[38].rating}\n"
                                                f"40. {registeredPlayers[39].name} - {registeredPlayers[39].rating}```")
    except:
        await interaction.response.send_message(
            "There are not 40 registered players yet so the leaderboard will not send.")


@bot.tree.command(name="lb2", description="Displays the second page of the Leaderboard")
async def lb2(interaction: discord.Interaction):
    global registeredPlayers
    #Check that we have at least 80 players so we don't access an index that wasn't created
    #Same notes as above about ugly code
    if (len(registeredPlayers) > 80):
        await interaction.response.send_message(
            f"```41. {registeredPlayers[40].name} - {registeredPlayers[40].rating}\n"
            f"42. {registeredPlayers[41].name} - {registeredPlayers[41].rating}\n"
            f"43. {registeredPlayers[42].name} - {registeredPlayers[42].rating}\n"
            f"44. {registeredPlayers[43].name} - {registeredPlayers[43].rating}\n"
            f"45. {registeredPlayers[44].name} - {registeredPlayers[44].rating}\n"
            f"46. {registeredPlayers[45].name} - {registeredPlayers[45].rating}\n"
            f"47. {registeredPlayers[46].name} - {registeredPlayers[46].rating}\n"
            f"48. {registeredPlayers[47].name} - {registeredPlayers[47].rating}\n"
            f"49. {registeredPlayers[48].name} - {registeredPlayers[48].rating}\n"
            f"50. {registeredPlayers[49].name} - {registeredPlayers[49].rating}\n"
            f"51. {registeredPlayers[50].name} - {registeredPlayers[50].rating}\n"
            f"52. {registeredPlayers[51].name} - {registeredPlayers[51].rating}\n"
            f"53. {registeredPlayers[52].name} - {registeredPlayers[52].rating}\n"
            f"54. {registeredPlayers[53].name} - {registeredPlayers[53].rating}\n"
            f"55. {registeredPlayers[54].name} - {registeredPlayers[54].rating}\n"
            f"56. {registeredPlayers[55].name} - {registeredPlayers[55].rating}\n"
            f"57. {registeredPlayers[56].name} - {registeredPlayers[56].rating}\n"
            f"58. {registeredPlayers[57].name} - {registeredPlayers[57].rating}\n"
            f"59. {registeredPlayers[58].name} - {registeredPlayers[58].rating}\n"
            f"60. {registeredPlayers[59].name} - {registeredPlayers[59].rating}\n"
            f"61. {registeredPlayers[60].name} - {registeredPlayers[60].rating}\n"
            f"62. {registeredPlayers[61].name} - {registeredPlayers[61].rating}\n"
            f"63. {registeredPlayers[62].name} - {registeredPlayers[62].rating}\n"
            f"64. {registeredPlayers[63].name} - {registeredPlayers[63].rating}\n"
            f"65. {registeredPlayers[64].name} - {registeredPlayers[64].rating}\n"
            f"66. {registeredPlayers[65].name} - {registeredPlayers[65].rating}\n"
            f"67. {registeredPlayers[66].name} - {registeredPlayers[66].rating}\n"
            f"68. {registeredPlayers[67].name} - {registeredPlayers[67].rating}\n"
            f"69. {registeredPlayers[68].name} - {registeredPlayers[68].rating}\n"
            f"70. {registeredPlayers[69].name} - {registeredPlayers[69].rating}\n"
            f"71. {registeredPlayers[70].name} - {registeredPlayers[70].rating}\n"
            f"72. {registeredPlayers[71].name} - {registeredPlayers[71].rating}\n"
            f"73. {registeredPlayers[72].name} - {registeredPlayers[72].rating}\n"
            f"74. {registeredPlayers[73].name} - {registeredPlayers[73].rating}\n"
            f"75. {registeredPlayers[74].name} - {registeredPlayers[74].rating}\n"
            f"76. {registeredPlayers[75].name} - {registeredPlayers[75].rating}\n"
            f"77. {registeredPlayers[76].name} - {registeredPlayers[76].rating}\n"
            f"78. {registeredPlayers[77].name} - {registeredPlayers[77].rating}\n"
            f"79. {registeredPlayers[78].name} - {registeredPlayers[78].rating}\n"
            f"80. {registeredPlayers[79].name} - {registeredPlayers[79].rating}```")
    else:
        await interaction.response.send_message("Not enough players to display leaderboard 2\n")


@bot.tree.command(name="lb3", description="Displays the third page of the Leaderboard")
async def lb3(interaction: discord.Interaction):
    global registeredPlayers
    #Same notes as lb2
    if (len(registeredPlayers) >= 120):
        await interaction.response.send_message(
            f"```81. {registeredPlayers[80].name} - {registeredPlayers[80].rating}\n"
            f"82. {registeredPlayers[81].name} - {registeredPlayers[81].rating}\n"
            f"83. {registeredPlayers[82].name} - {registeredPlayers[82].rating}\n"
            f"84. {registeredPlayers[83].name} - {registeredPlayers[83].rating}\n"
            f"85. {registeredPlayers[84].name} - {registeredPlayers[84].rating}\n"
            f"86. {registeredPlayers[85].name} - {registeredPlayers[85].rating}\n"
            f"87. {registeredPlayers[86].name} - {registeredPlayers[86].rating}\n"
            f"88. {registeredPlayers[87].name} - {registeredPlayers[87].rating}\n"
            f"89. {registeredPlayers[88].name} - {registeredPlayers[88].rating}\n"
            f"90. {registeredPlayers[89].name} - {registeredPlayers[89].rating}\n"
            f"91. {registeredPlayers[90].name} - {registeredPlayers[90].rating}\n"
            f"92. {registeredPlayers[91].name} - {registeredPlayers[91].rating}\n"
            f"93. {registeredPlayers[92].name} - {registeredPlayers[92].rating}\n"
            f"94. {registeredPlayers[93].name} - {registeredPlayers[93].rating}\n"
            f"95. {registeredPlayers[94].name} - {registeredPlayers[94].rating}\n"
            f"96. {registeredPlayers[95].name} - {registeredPlayers[95].rating}\n"
            f"97. {registeredPlayers[96].name} - {registeredPlayers[96].rating}\n"
            f"98. {registeredPlayers[97].name} - {registeredPlayers[97].rating}\n"
            f"99. {registeredPlayers[98].name} - {registeredPlayers[98].rating}\n"
            f"100. {registeredPlayers[99].name} - {registeredPlayers[99].rating}\n"
            f"101. {registeredPlayers[100].name} - {registeredPlayers[100].rating}\n"
            f"102. {registeredPlayers[101].name} - {registeredPlayers[101].rating}\n"
            f"103. {registeredPlayers[102].name} - {registeredPlayers[102].rating}\n"
            f"104. {registeredPlayers[103].name} - {registeredPlayers[103].rating}\n"
            f"105. {registeredPlayers[104].name} - {registeredPlayers[104].rating}\n"
            f"106. {registeredPlayers[105].name} - {registeredPlayers[105].rating}\n"
            f"107. {registeredPlayers[106].name} - {registeredPlayers[106].rating}\n"
            f"108. {registeredPlayers[107].name} - {registeredPlayers[107].rating}\n"
            f"109. {registeredPlayers[108].name} - {registeredPlayers[108].rating}\n"
            f"110. {registeredPlayers[109].name} - {registeredPlayers[109].rating}\n"
            f"111. {registeredPlayers[110].name} - {registeredPlayers[110].rating}\n"
            f"112. {registeredPlayers[111].name} - {registeredPlayers[111].rating}\n"
            f"113. {registeredPlayers[112].name} - {registeredPlayers[112].rating}\n"
            f"114. {registeredPlayers[113].name} - {registeredPlayers[113].rating}\n"
            f"115. {registeredPlayers[114].name} - {registeredPlayers[114].rating}\n"
            f"116. {registeredPlayers[115].name} - {registeredPlayers[115].rating}\n"
            f"117. {registeredPlayers[116].name} - {registeredPlayers[116].rating}\n"
            f"118. {registeredPlayers[117].name} - {registeredPlayers[117].rating}\n"
            f"119. {registeredPlayers[118].name} - {registeredPlayers[118].rating}\n"
            f"120. {registeredPlayers[119].name} - {registeredPlayers[119].rating}```")
    else:
        await interaction.response.send_message("Not enough players to display leaderboard 3\n")

#Function deletes a user from the data, opposite of registering a player
#Params: Takes a username as a string
@bot.tree.command(name="delete", description="Delete a registered player")
@app_commands.describe(username="Delete a player")
@app_commands.checks.has_role("Ranked Staff")
async def delete(interaction: discord.Interaction, username: str):
    global registeredPlayers
    player = username
    #Iterate through our list of players to see if this user is registered
    for x in registeredPlayers:
        if player.lower() == x.name.lower():
            #Remove them from the list of users
            registeredPlayers.remove(x)
            #Sort the list by rating from highest to lowest
            registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
            #Reassign ranks
            for i in range(len(registeredPlayers)):
                registeredPlayers[i].rank = i + 1
            await interaction.response.send_message(f"{player} has been removed")
            return

#This function parses a text file to add to and update player statistics
#Params: Takes a text file as a string, the text file must be one produced from Podcrash using /pdc exportstats
#Params: User must have the "Ranked Staff" role, otherwise the command will not work
@bot.tree.command(name="addstats", description="Add stats to the bot")
@app_commands.describe(stats="Add the stats")
@app_commands.checks.has_role("Ranked Staff")
async def addstats(ctx, stats: str):
    global registeredPlayers, alleyInt, atomInt, mirageInt, carrierInt, cobbleInt, trainInt, opInt, ogInt, cacheInt, templeInt, ancientInt, sandInt
    #Create 2 Arrays so I can separate the players into 2 teams
    teamOne = []
    teamTwo = []
    #Counter is updated to make sure that the function found 10 players, if not it disregards the stats because there must have been a mistake
    counter = 0
    #If winner is 0 then team A won, if winner is 1 then team B won
    winner = 2
    #Rounds keeps track of how many rounds were played that game
    rounds = 0
    #Split the text file into an array where each index is one word
    stat = stats.split()

    for y in range(len(stat)):

        #If we find "A" we know the amount of rounds A team won is the next string
        if stat[y] == "A":
            a = stat[y + 1]
            #Add the amount of rounds A won to the total number of rounds
            rounds += int(a)
            #If A is 12 then we know team A won the game so we declare them the winner
            if a == "12":
                winner = 0

        #If we find "B" we know the amount of rounds A team won is the next string
        if stat[y] == "B":
            b = stat[y + 1]
            # Add the amount of rounds B won to the total number of rounds
            rounds += int(b)
            # If B is 12 then we know team B won the game so we declare them the winner
            if b == "12":
                winner = 1
        #If we find the word "Crims", we know in 2 words from now it will be the map
        if stat[y] == "Crims":
            #Compare strings to see if the map matches, if it does increase the amount it's been played by 1
            c = stat[y + 2]
            if c.lower() == alley.lower():
                alleyInt += 1
            elif c.lower() == atom.lower():
                atomInt += 1
            elif c.lower() == mirage.lower():
                mirageInt += 1
            elif c.lower() == carrier.lower():
                carrierInt += 1
            elif c.lower() == cobble.lower():
                cobbleInt += 1
            elif c.lower() == train.lower():
                trainInt += 1
            elif c.lower() == op.lower():
                opInt += 1
            elif c.lower() == og.lower():
                ogInt += 1
            elif c.lower() == cache.lower():
                cacheInt += 1
            elif c.lower() == ancient.lower():
                ancientInt += 1
            elif c.lower() == sand.lower():
                sandInt += 1
            elif c.lower() == temple.lower():
                templeInt += 1
            else:
                #If we couldn't find the maps, let them know (normally there will be a spelling issue as map name is manually added to the text)
                await ctx.response.send_message(
                    "Map not found, try again (use /maps for correct spellings)")
                return

    for i in range(len(stat)):
        for x in registeredPlayers:
            if stat[i].lower() == x.name.lower():
                #Iterate until we find a username, the first 5 usernames go to Team A, the last 5 usernames go to Team B
                if (counter < 5):
                    teamOne.append(x.name)
                    counter += 1
                else:
                    teamTwo.append(x.name)
                    counter += 1
                #If the user is in team A and they won, they gain 12 ELO
                if x.name in teamOne and winner == 0:
                    ELO = 12
                #If the user is in team A and they lost, they lose 12 ELO
                elif x.name in teamOne and winner == 1:
                    ELO = -12
                #If the user is in team B and they won, they gain 12 ELO
                elif x.name in teamTwo and winner == 0:
                    ELO = -12
                #If the user is in team B and they lost, they lose 12 ELO
                elif x.name in teamTwo and winner == 1:
                    ELO = 12
                #kd is an array with the kills and deaths (ex: [17, 14])
                kd = stat[i + 1].split("-")

                #If the user has played less than 100 games, the formula is different
                if x.gp < 100:
                    #Elo gained in game: previousELO + ((kills - deaths) +/- 12) (depending on win or lose)
                    formula = x.rating + (int(kd[0]) - int(kd[1]) + ELO)
                else:
                    #outcome: previousELO + ((elo gained in game) - (expected performance))
                    #expected performance: ((total kills - total deaths) + 12*(total wins - total losses))/games played
                    formula = x.rating + (
                            (int(kd[0]) - int(kd[1]) + ELO) - ((x.kills - x.deaths) + 12 * (x.wins - x.losses)) / (
                            x.wins + x.losses))
                #Update this users kills, deaths, kdr, rounds played, games played
                x.kills += int(kd[0])
                x.deaths += int(kd[1])
                x.kdr = round(x.kills / x.deaths, 3)
                x.rp += rounds
                x.gp += 1
                #Avoid divide by 0 errors to set the kills per round
                if (x.rp > 0):
                    x.kpr = round(x.kills / x.rp, 3)
                #If they gained 12 ELO they won so increase their wins by 1, otherwise increase losses by 1
                if ELO == 12:
                    x.wins += 1
                if ELO == -12:
                    x.losses += 1
                #Update the win loss rating and update their current rating
                x.wlr = round((x.wins / x.gp) * 100, 3)
                x.rating = round(formula, 3)
    if counter != 10:
        #If we didn't iterate through 10 users, automatically remove the stats that were just input and return
        await removestatshelper(ctx, message=stat)
        return
    #If everything went right, sort the list by rating and sort ranks
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1
    await ctx.response.send_message("Stats Added!")

#This function parses a text file to subtract from and update player statistics
#Params: Takes a text file as a string, the text file must be one produced from Podcrash using /pdc exportstats
#Params: User must have the "Ranked Staff" role, otherwise the command will not work
#Note: The code comments are the exact same as the previous function but instead of adding we are subtracting
@bot.tree.command(name="removestats", description="Remove stats from the bot")
@app_commands.describe(stats="Remove the stats")
@app_commands.checks.has_role("Ranked Staff")
async def removestats(interaction: discord.Interaction, stats: str):
    global registeredPlayers, alleyInt, atomInt, mirageInt, carrierInt, cobbleInt, trainInt, opInt, ogInt, cacheInt, templeInt, ancientInt, sandInt
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    rounds = 0
    stat = stats.split()
    for y in range(len(stat)):
        if stat[y] == "A":
            a = stat[y + 1]
            rounds += int(a)
            if a == "12":
                winner = 0
        if stat[y] == "B":
            b = stat[y + 1]
            rounds += int(b)
            if b == "12":
                winner = 1
        if stat[y] == "Crims":
            c = stat[y + 2]
            if c.lower() == alley.lower():
                alleyInt -= 1
            elif c.lower() == atom.lower():
                atomInt -= 1
            elif c.lower() == mirage.lower():
                mirageInt -= 1
            elif c.lower() == carrier.lower():
                carrierInt -= 1
            elif c.lower() == cobble.lower():
                cobbleInt -= 1
            elif c.lower() == train.lower():
                trainInt -= 1
            elif c.lower() == op.lower():
                opInt -= 1
            elif c.lower() == og.lower():
                ogInt -= 1
            elif c.lower() == cache.lower():
                cacheInt -= 1
            elif c.lower() == ancient.lower():
                ancientInt -= 1
            elif c.lower() == sand.lower():
                sandInt -= 1
            elif c.lower() == temple.lower():
                templeInt -= 1

    for i in range(len(stat)):
        for x in registeredPlayers:
            if stat[i].lower() == x.name.lower():
                if (counter < 5):
                    teamOne.append(x.name)
                    counter += 1
                else:
                    teamTwo.append(x.name)
                    counter += 1
                if x.name in teamOne and winner == 0:
                    ELO = 12
                elif x.name in teamOne and winner == 1:
                    ELO = -12
                elif x.name in teamTwo and winner == 0:
                    ELO = -12
                elif x.name in teamTwo and winner == 1:
                    ELO = 12
                kd = stat[i + 1].split("-")

                if (x.wins + x.losses) < 100:
                    formula = x.rating - (int(kd[0]) - int(kd[1]) + ELO)
                else:
                    formula = x.rating - (
                            (int(kd[0]) - int(kd[1]) + ELO) - ((x.kills - x.deaths) + 12 * (x.wins - x.losses)) / (
                            x.wins + x.losses))

                x.kills -= int(kd[0])
                x.deaths -= int(kd[1])
                x.rp -= rounds
                x.gp -= 1
                if (x.deaths == 0):
                    x.kdr = 0
                elif (x.deaths > 0):
                    x.kdr = round(x.kills / x.deaths, 3)
                if (x.rp > 0):
                    x.kpr = round(x.kills / x.rp, 3)
                if ELO == 12:
                    x.wins -= 1
                if ELO == -12:
                    x.losses -= 1
                if x.gp != 0:
                    x.wlr = round((x.wins / x.gp) * 100, 3)
                else:
                    x.wlr = 0
                x.rating = round(formula, 3)
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1
    await interaction.response.send_message("Stats Removed!")

#This command was created due to technicalities with calling removestats within another command
#It does the exact same thing as the removestats command
async def removestatshelper(ctx, *, message):
    global registeredPlayers, alleyInt, atomInt, mirageInt, carrierInt, cobbleInt, trainInt, opInt, ogInt, cacheInt, templeInt, ancientInt, sandInt
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    rounds = 0
    stats = message
    for y in range(len(stats)):
        if stats[y] == "A":
            a = stats[y + 1]
            rounds += int(a)
            if a == "12":
                winner = 0
        if stats[y] == "B":
            b = stats[y + 1]
            rounds += int(b)
            if b == "12":
                winner = 1
        if stats[y] == "Crims":
            c = stats[y + 2]
            if c.lower() == alley.lower():
                alleyInt -= 1
            elif c.lower() == atom.lower():
                atomInt -= 1
            elif c.lower() == mirage.lower():
                mirageInt -= 1
            elif c.lower() == carrier.lower():
                carrierInt -= 1
            elif c.lower() == cobble.lower():
                cobbleInt -= 1
            elif c.lower() == train.lower():
                trainInt -= 1
            elif c.lower() == op.lower():
                opInt -= 1
            elif c.lower() == og.lower():
                ogInt -= 1
            elif c.lower() == cache.lower():
                cacheInt -= 1
            elif c.lower() == ancient.lower():
                ancientInt -= 1
            elif c.lower() == sand.lower():
                sandInt -= 1
            elif c.lower() == temple.lower():
                templeInt -= 1

    for i in range(len(stats)):
        for x in registeredPlayers:
            if stats[i].lower() == x.name.lower():
                if (counter < 5):
                    teamOne.append(x.name)
                    counter += 1
                else:
                    teamTwo.append(x.name)
                    counter += 1
                if x.name in teamOne and winner == 0:
                    ELO = 12
                elif x.name in teamOne and winner == 1:
                    ELO = -12
                elif x.name in teamTwo and winner == 0:
                    ELO = -12
                elif x.name in teamTwo and winner == 1:
                    ELO = 12
                kd = stats[i + 1].split("-")

                if (x.wins + x.losses) < 100:
                    formula = x.rating - (int(kd[0]) - int(kd[1]) + ELO)
                else:
                    formula = x.rating - (
                            (int(kd[0]) - int(kd[1]) + ELO) - ((x.kills - x.deaths) + 12 * (x.wins - x.losses)) / (
                            x.wins + x.losses))

                x.kills -= int(kd[0])
                x.deaths -= int(kd[1])
                x.rp -= rounds
                x.gp -= 1
                if (x.deaths == 0):
                    x.kdr = 0
                elif (x.deaths > 0):
                    x.kdr = round(x.kills / x.deaths, 3)
                if (x.rp > 0):
                    x.kpr = round(x.kills / x.rp, 3)
                if ELO == 12:
                    x.wins -= 1
                if ELO == -12:
                    x.losses -= 1
                if x.gp != 0:
                    x.wlr = round((x.wins / x.gp) * 100, 3)
                else:
                    x.wlr = 0
                x.rating = round(formula, 3)
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1
    await ctx.response.send_message("Warning: Stats were entered with an unregistered player\n"
                                    "Stats were automatically removed, register all players, and then re-enter the stats")

#Command to change a registered player's username
#Params: Takes a username as a string
#Params: User must have the Ranked Staff role to use this command
@bot.tree.command(name="changename", description="Change the first name to the second")
@app_commands.describe(oldname="Original Username", newname="New Username")
@app_commands.checks.has_role("Ranked Staff")
async def changename(interaction: discord.Interaction, oldname: str, newname: str):
    global registeredPlayers
    #Set the old name to name1 and set the new name to name2
    name1 = oldname
    name2 = newname
    #Boolean for if we changed the name successfully
    true = 0

    for x in registeredPlayers:
        #If the new name is the same as the old one, and it's in the system, change the name from the list to the new one
        #Purpose of this is to fix capitalization on usernames
        if (name2.lower() == name1.lower() and name2.lower() == x.name.lower()):
            x.name = name2
            await interaction.response.send_message(f"'{oldname}' changed to '{newname}'")
            return
        #If the new name is already in the system that is a duplicate so we return
        if name2.lower() == x.name.lower():
            await interaction.response.send_message(f"'{newname}' is already in use")
            return
    for x in registeredPlayers:
        #I don't think I needed to use a second loop honestly, next time I update the bot I'll fix this
        #Should have just added an and to the part above
        #If the old name is in the list, update it to the new name, set the flag and send a message
        if name1.lower() == x.name.lower():
            x.name = name2
            true = 1
            await interaction.response.send_message(f"'{oldname}' changed to '{newname}'")

    if true == 0:
        await interaction.response.send_message("Error: Failed to change name")

#This command manually sets a players stats
#Params: (Read the .describe bit)
#Params: User must have the "Admin" role for this command to work
@bot.tree.command(name="set", description="Manually set a player's stats")
@app_commands.describe(name="Username", kills="Kills", deaths="Deaths", kdr="KDR (float)", wins="Wins", losses="Losses", rank="Rank", rating="Rating",
                       gp="Games Played", wlr="Win/Loss Rating (float)", rp="Rounds Played", kpr="Kills/Round (float)")
@app_commands.checks.has_role("Admin")
async def set(interaction: discord.Interaction, name: str, kills: int, deaths: int, kdr: float, wins: int, losses: int, rank: int, rating: int,
              gp: int, wlr: float, rp: int, kpr: float):
    global registeredPlayers
    for x in registeredPlayers:
        if name == x.name:
            x.kills = kills
            x.deaths = deaths
            x.kdr = kdr
            x.wins = wins
            x.losses = losses
            x.rank = rank
            x.rating = rating
            x.gp = gp
            x.wlr = wlr
            x.rp = rp
            x.kpr = kpr
            await interaction.response.send_message(f"Set {name}'s stats")
            return
    await interaction.response.send_message("Error: Failed to set stats")

#This command prints out a players stats
#Different from -r as this just prints every stat we collect in a single line, -r doesn't print everything
#Params: Takes in a username as a string
#Params: User must have the "Admin" role to run this command
@bot.tree.command(name="get", description="See all of a player's stats")
@app_commands.describe(name="Username")
@app_commands.checks.has_role("Admin")
async def get(interaction: discord.Interaction, name: str):
    global registeredPlayers
    for x in registeredPlayers:
        if name.lower() == x.name.lower():
            await interaction.response.send_message(f"Username: {x.name}, Kills: {x.kills}, Deaths: {x.deaths}, kdr: {x.kdr}, Wins: {x.wins}, "
                                                    f"Losses: {x.losses}, Rank: {x.rank}, Rating: {x.rating}, Games Played: {x.gp}, wlr: {x.wlr}%, "
                                                    f"Rounds Played: {x.rp}, kpr: {x.kpr}")
            return
    await interaction.response.send_message("Player not found")

#The botban command checks if a player's stats are low enough to deserve being temporarily banned from Ranked CvC
#This rule is not currently in effect, but there was a point where if you were bad enough at the game, you were forced to take a break
#So that you wouldn't ruin queues by being significantly worse than everyone else
#Params: User must have the "Ranked Staff" role to run this command
@bot.tree.command(name="botban", description="See who needs a botban")
@app_commands.checks.has_role("Ranked Staff")
async def botban(interaction: discord.Interaction):
    global registeredPlayers
    #A player has 5 games to get their stats up post bot ban, this is just a warning message
    await interaction.response.send_message(
        "Warning: This does not take into account if it has been 5 games since a players last bot ban\n")
    for x in registeredPlayers:
        #Two ways to get bot banned:
        #Play at least 10 games with a kd < 0.5 and win/loss less than 50% OR
        #Play at least 5 games and have a kd < 0.4
        if x.gp >= 10 and x.kdr < 0.5 and x.wlr < 0.5:
            await interaction.followup.send(
                f"{x.name} needs a bot ban (KDR: {x.kdr}) and WL: {x.wlr * 100}%\n")
        elif x.gp >= 5 and x.kdr < 0.4:
            await interaction.followup.send(
                f"{x.name} needs a bot ban (KDR: {x.kdr}) and WL: {x.wlr * 100}%\n")

#This command goes through our list of players and sets everyones stats to the default
#This would be used at the start of the season in the event we did not need to take the bot down for updates (very rare)
#Params: User must have the "Admin" role
@bot.tree.command(name="resetseasonrankedcvc", description="Resets the season")
@app_commands.checks.has_role("Admin")
async def resetseasonrankedcvc(interaction: discord.Interaction):
    global registeredPlayers, alleyInt, atomInt, mirageInt, carrierInt, cobbleInt, trainInt, opInt, ogInt, cacheInt, ancientInt, sandInt, templeInt
    for i in registeredPlayers:
        i.kills = 0
        i.deaths = 0
        i.kdr = 0
        i.wins = 0
        i.losses = 0
        i.rating = 1500
        i.gp = 0
        i.wlr = 0
        i.rp = 0
        i.kpr = 0
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1
    alleyInt = atomInt = mirageInt = carrierInt = cobbleInt = trainInt = opInt = ogInt = cacheInt = ancientInt = sandInt = templeInt = 0
    await interaction.response.send_message("Oh boy, hope you meant to do that")

#This command subtracts 20 rating from a player
#Params: Takes a username as a string
#Params: User must be "Ranked Staff" to run this command
@bot.tree.command(name="minus20", description="Subtract 20 elo from a player")
@app_commands.describe(name="Username")
@app_commands.checks.has_role("Ranked Staff")
async def minus20(interaction: discord.Interaction, name: str):
    global registeredPlayers
    for x in registeredPlayers:
        if name.lower() == x.name.lower():
            #If we find the player, subtract 20 rating
            x.rating -= 20
            #Sort all the players by rating as the leaderboard may have changed and update ranks
            registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
            for i in range(len(registeredPlayers)):
                registeredPlayers[i].rank = i + 1
            await interaction.response.send_message(f"20 elo has been removed from {x.name}")
            return

    #Something must have gone wrong if we are here
    await interaction.response.send_message(f"Invalid username")

#This command adds 20 rating to a player
#Params: Takes a username as a string
#Params: User must be "Ranked Staff" to run this command
#Note: add20 was written months before minus20 and it really shows in the code
@bot.tree.command(name="add20", description="Add 20 elo from a player")
@app_commands.describe(name="Username")
@app_commands.checks.has_role("Ranked Staff")
async def add20(interaction: discord.Interaction, name: str):
    global registeredPlayers
    try:
        for x in registeredPlayers:
            if name.lower() == x.name.lower():
                #If we find the user, add 20 rating
                x.rating += 20
                # Sort all the players by rating as the leaderboard may have changed and update ranks
                registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
                for i in range(len(registeredPlayers)):
                    registeredPlayers[i].rank = i + 1
                await interaction.response.send_message(f"20 elo has been added to {x.name}")
    except:
        raise error

#This command adds and updates stats to the players, but only to those who won the game
#The reason for using this is that a player on the losing team disconnected from the game early on which affected the outcome
#Params: Takes in a text file as a string of the stats generated by the Podcrash command /pdc exportstats
#Params: User must have the role "Ranked Staff" to run this command
#Note: See the "addstats" command for functionality on how this works, only difference here is that we update the stats
#Only if we know that the user was a part of the winning team
@bot.tree.command(name="addstatsnoeloloss", description="Add stats without harm to the losers")
@app_commands.describe(stats="Stats")
@app_commands.checks.has_role("Ranked Staff")
async def addstatsnoeloloss(ctx, stats: str):
    global registeredPlayers, alleyInt, atomInt, mirageInt, carrierInt, cobbleInt, trainInt, opInt, ogInt, cacheInt, templeInt, ancientInt, sandInt
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    rounds = 0
    stat = stats.split()
    for y in range(len(stat)):
        if stat[y] == "A":
            a = stat[y + 1]
            rounds += int(a)
            if a == "12":
                winner = 0
        if stat[y] == "B":
            b = stat[y + 1]
            rounds += int(b)
            if b == "12":
                winner = 1
        if stat[y] == "Crims":
            c = stat[y + 2]
            if c.lower() == alley.lower():
                alleyInt += 1
            elif c.lower() == atom.lower():
                atomInt += 1
            elif c.lower() == mirage.lower():
                mirageInt += 1
            elif c.lower() == carrier.lower():
                carrierInt += 1
            elif c.lower() == cobble.lower():
                cobbleInt += 1
            elif c.lower() == train.lower():
                trainInt += 1
            elif c.lower() == op.lower():
                opInt += 1
            elif c.lower() == og.lower():
                ogInt += 1
            elif c.lower() == cache.lower():
                cacheInt += 1
            elif c.lower() == ancient.lower():
                ancientInt += 1
            elif c.lower() == sand.lower():
                sandInt += 1
            elif c.lower() == temple.lower():
                templeInt += 1
            else:
                await ctx.response.send_message("Map not found, try again (use /mapplays for correct spelling)")
                return
    for i in range(len(stat)):
        for x in registeredPlayers:
            if stat[i].lower() == x.name.lower():
                if (counter < 5):
                    teamOne.append(x.name)
                    counter += 1
                else:
                    teamTwo.append(x.name)
                    counter += 1
                if x.name in teamOne and winner == 0:
                    ELO = 12
                elif x.name in teamOne and winner == 1:
                    ELO = -12
                elif x.name in teamTwo and winner == 0:
                    ELO = -12
                elif x.name in teamTwo and winner == 1:
                    ELO = 12
                kd = stat[i + 1].split("-")

                if (x.wins + x.losses) < 101:
                    formula = x.rating + (int(kd[0]) - int(kd[1]) + ELO)
                else:
                    formula = x.rating + (
                            (int(kd[0]) - int(kd[1]) + ELO) - ((x.kills - x.deaths) + 12 * (x.wins - x.losses)) / (
                            x.wins + x.losses))
                if (ELO == 12):
                    x.kills += int(kd[0])
                    x.deaths += int(kd[1])
                    x.rp += rounds
                    x.gp += 1
                    x.kdr = round(x.kills / x.deaths, 3)
                    if x.rp > 0:
                        x.kpr = round(x.kills / x.rp, 3)
                    if ELO == 12:
                        x.wins += 1
                    if ELO == -12:
                        x.losses += 1
                    x.wlr = round((x.wins / x.gp) * 100, 3)
                    x.rating = round(formula, 3)
    if counter != 10:
        await removestatsnoelolosshelper(ctx, message=stat)
        return
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1
    await ctx.response.send_message("Stats Added!")

#This command removes and updates stats to the players, but only to those who won the game
#This is a helper command to addstatsnoeloloss, it removes stats but only from those who won the game
#Params: Takes in a text file as a string of the stats generated by the Podcrash command /pdc exportstats
#Params: User must have the role "Ranked Staff" to run this command
#Note: See the "addstats" command for functionality on how this works, only difference here is that we update the stats
#Only if we know that the user was a part of the winning team, and also we subtract instead of add
async def removestatsnoelolosshelper(ctx,*,message):
    global registeredPlayers, alleyInt, atomInt, mirageInt, carrierInt, cobbleInt, trainInt, opInt, ogInt, cacheInt, templeInt, ancientInt, sandInt
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    rounds = 0
    stats = message
    for y in range(len(stats)):
        if stats[y] == "A":
            a = stats[y + 1]
            rounds += int(a)
            if a == "12":
                winner = 0
        if stats[y] == "B":
            b = stats[y + 1]
            rounds += int(b)
            if b == "12":
                winner = 1
        if stats[y] == "Crims":
            c = stats[y + 2]
            if c.lower() == alley.lower():
                alleyInt -= 1
            elif c.lower() == atom.lower():
                atomInt -= 1
            elif c.lower() == mirage.lower():
                mirageInt -= 1
            elif c.lower() == carrier.lower():
                carrierInt -= 1
            elif c.lower() == cobble.lower():
                cobbleInt -= 1
            elif c.lower() == train.lower():
                trainInt -= 1
            elif c.lower() == op.lower():
                opInt -= 1
            elif c.lower() == og.lower():
                ogInt -= 1
            elif c.lower() == cache.lower():
                cacheInt -= 1
            elif c.lower() == ancient.lower():
                ancientInt -= 1
            elif c.lower() == sand.lower():
                sandInt -= 1
            elif c.lower() == temple.lower():
                templeInt -= 1
    for i in range(len(stats)):
        for x in registeredPlayers:
            if stats[i].lower() == x.name.lower():
                if (counter < 5):
                    teamOne.append(x.name)
                    counter += 1
                else:
                    teamTwo.append(x.name)
                    counter += 1
                if x.name in teamOne and winner == 0:
                    ELO = 12
                elif x.name in teamOne and winner == 1:
                    ELO = -12
                elif x.name in teamTwo and winner == 0:
                    ELO = -12
                elif x.name in teamTwo and winner == 1:
                    ELO = 12
                kd = stats[i + 1].split("-")

                if (x.wins + x.losses) < 100:
                    formula = x.rating - (int(kd[0]) - int(kd[1]) + ELO)
                else:
                    formula = x.rating - (
                            (int(kd[0]) - int(kd[1]) + ELO) - ((x.kills - x.deaths) + 12 * (x.wins - x.losses)) / (
                            x.wins + x.losses))

                if(ELO == 12):
                    x.kills -= int(kd[0])
                    x.deaths -= int(kd[1])
                    x.rp -= rounds
                    x.gp -= 1
                    if (x.deaths == 0):
                        x.kdr = 0
                    elif(x.deaths > 0):
                        x.kdr = round(x.kills / x.deaths, 3)
                    if(x.rp > 0):
                        x.kpr = round(x.kills/x.rp, 3)
                    if ELO == 12:
                        x.wins -= 1
                    if ELO == -12:
                        x.losses += 1
                    if x.gp != 0:
                        x.wlr = round((x.wins / x.gp) * 100, 3)
                    else:
                        x.wlr = 0
                    x.rating = round(formula, 3)
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1
    await ctx.response.send_message("Warning: Stats were entered with an unregistered player\n"
                                    "Stats were automatically removed, register all players, and then re-enter the stats")

#This command removes and updates stats to the players, but only to those who won the game
#Params: Takes in a text file as a string of the stats generated by the Podcrash command /pdc exportstats
#Params: User must have the role "Ranked Staff" to run this command
#Note: See the "addstats" command for functionality on how this works, only difference here is that we update the stats
#Only if we know that the user was a part of the winning team, and we subtract instead of add
@bot.tree.command(name="removestatsnoeloloss", description="Remove stats from a no elo loss game")
@app_commands.describe(stats="Stats")
@app_commands.checks.has_role("Ranked Staff")
async def removestatsnoeloloss(interaction: discord.Interaction, stats: str):
    global registeredPlayers, alleyInt, atomInt, mirageInt, carrierInt, cobbleInt, trainInt, opInt, ogInt, cacheInt, templeInt, ancientInt, sandInt
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    rounds = 0
    stat = stats.split()
    for y in range(len(stat)):
        if stat[y] == "A":
            a = stat[y + 1]
            rounds += int(a)
            if a == "12":
                winner = 0
        if stat[y] == "B":
            b = stat[y + 1]
            rounds += int(b)
            if b == "12":
                winner = 1
        if stat[y] == "Crims":
            c = stats[y + 2]
            if c.lower() == alley.lower():
                alleyInt -= 1
            elif c.lower() == atom.lower():
                atomInt -= 1
            elif c.lower() == mirage.lower():
                mirageInt -= 1
            elif c.lower() == carrier.lower():
                carrierInt -= 1
            elif c.lower() == cobble.lower():
                cobbleInt -= 1
            elif c.lower() == train.lower():
                trainInt -= 1
            elif c.lower() == op.lower():
                opInt -= 1
            elif c.lower() == og.lower():
                ogInt -= 1
            elif c.lower() == cache.lower():
                cacheInt -= 1
            elif c.lower() == ancient.lower():
                ancientInt -= 1
            elif c.lower() == sand.lower():
                sandInt -= 1
            elif c.lower() == temple.lower():
                templeInt -= 1
    for i in range(len(stat)):
        for x in registeredPlayers:
            if stat[i].lower() == x.name.lower():
                if (counter < 5):
                    teamOne.append(x.name)
                    counter += 1
                else:
                    teamTwo.append(x.name)
                    counter += 1
                if x.name in teamOne and winner == 0:
                    ELO = 12
                elif x.name in teamOne and winner == 1:
                    ELO = -12
                elif x.name in teamTwo and winner == 0:
                    ELO = -12
                elif x.name in teamTwo and winner == 1:
                    ELO = 12
                kd = stat[i + 1].split("-")

                if (x.wins + x.losses) < 100:
                    formula = x.rating - (int(kd[0]) - int(kd[1]) + ELO)
                else:
                    formula = x.rating - (
                            (int(kd[0]) - int(kd[1]) + ELO) - ((x.kills - x.deaths) + 12 * (x.wins - x.losses)) / (
                            x.wins + x.losses))

                if (ELO == 12):
                    x.kills -= int(kd[0])
                    x.deaths -= int(kd[1])
                    x.rp -= rounds
                    x.gp -= 1
                    if (x.deaths == 0):
                        x.kdr = 0
                    elif (x.deaths > 0):
                        x.kdr = round(x.kills / x.deaths, 3)
                    if (x.rp > 0):
                        x.kpr = round(x.kills / x.rp, 3)
                    if ELO == 12:
                        x.wins -= 1
                    if ELO == -12:
                        x.losses += 1
                    if x.gp != 0:
                        x.wlr = round((x.wins / x.gp) * 100, 3)
                    else:
                        x.wlr = 0
                    x.rating = round(formula, 3)
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1
    await interaction.response.send_message("Stats Removed!")

#Note: Notes for this command apply to all top10 commands
@bot.tree.command(name="top10kills", description="Check the top 10 players with the most kills")
async def top10kills(interaction: discord.Interaction):
    global registeredPlayers
    #Create a temporary array to hold player data
    temp = []
    #Set the temporary array to our list of players, but it's sorted by most kills
    #I could loop the print statements but it would print one at a time which is ugly with slash commands and also inefficient
    temp = sorted(registeredPlayers, key=lambda Player: Player.kills, reverse=True)
    await interaction.response.send_message(f"`1: {temp[0].name} - {temp[0].kills}\n"
                                            f"2: {temp[1].name} - {temp[1].kills}\n"
                                            f"3: {temp[2].name} - {temp[2].kills}\n"
                                            f"4: {temp[3].name} - {temp[3].kills}\n"
                                            f"5: {temp[4].name} - {temp[4].kills}\n"
                                            f"6: {temp[5].name} - {temp[5].kills}\n"
                                            f"7: {temp[6].name} - {temp[6].kills}\n"
                                            f"8: {temp[7].name} - {temp[7].kills}\n"
                                            f"9: {temp[8].name} - {temp[8].kills}\n"
                                            f"10: {temp[9].name} - {temp[9].kills}`")

@bot.tree.command(name="top10deaths", description="Check the top 10 players with the most deaths")
async def top10deaths(interaction: discord.Interaction):
    global registeredPlayers
    temp = []
    temp = sorted(registeredPlayers, key=lambda Player: Player.deaths, reverse=True)
    await interaction.response.send_message(f"`1: {temp[0].name} - {temp[0].deaths}\n"
                                            f"2: {temp[1].name} - {temp[1].deaths}\n"
                                            f"3: {temp[2].name} - {temp[2].deaths}\n"
                                            f"4: {temp[3].name} - {temp[3].deaths}\n"
                                            f"5: {temp[4].name} - {temp[4].deaths}\n"
                                            f"6: {temp[5].name} - {temp[5].deaths}\n"
                                            f"7: {temp[6].name} - {temp[6].deaths}\n"
                                            f"8: {temp[7].name} - {temp[7].deaths}\n"
                                            f"9: {temp[8].name} - {temp[8].deaths}\n"
                                            f"10: {temp[9].name} - {temp[9].deaths}`")

@bot.tree.command(name="top10kdr", description="Check the top 10 kdrs")
async def top10kdr(interaction: discord.Interaction):
    global registeredPlayers
    temp = []
    temp = sorted(registeredPlayers, key=lambda Player: Player.kdr, reverse=True)
    await interaction.response.send_message(f"`1: {temp[0].name} - {temp[0].kdr}\n"
                                            f"2: {temp[1].name} - {temp[1].kdr}\n"
                                            f"3: {temp[2].name} - {temp[2].kdr}\n"
                                            f"4: {temp[3].name} - {temp[3].kdr}\n"
                                            f"5: {temp[4].name} - {temp[4].kdr}\n"
                                            f"6: {temp[5].name} - {temp[5].kdr}\n"
                                            f"7: {temp[6].name} - {temp[6].kdr}\n"
                                            f"8: {temp[7].name} - {temp[7].kdr}\n"
                                            f"9: {temp[8].name} - {temp[8].kdr}\n"
                                            f"10: {temp[9].name} - {temp[9].kdr}`")

@bot.tree.command(name="top10wins", description="Check the top 10 players with the most wins")
async def top10wins(interaction: discord.Interaction):
    global registeredPlayers
    temp = []
    temp = sorted(registeredPlayers, key=lambda Player: Player.wins, reverse=True)
    await interaction.response.send_message(f"`1: {temp[0].name} - {temp[0].wins}\n"
                                            f"2: {temp[1].name} - {temp[1].wins}\n"
                                            f"3: {temp[2].name} - {temp[2].wins}\n"
                                            f"4: {temp[3].name} - {temp[3].wins}\n"
                                            f"5: {temp[4].name} - {temp[4].wins}\n"
                                            f"6: {temp[5].name} - {temp[5].wins}\n"
                                            f"7: {temp[6].name} - {temp[6].wins}\n"
                                            f"8: {temp[7].name} - {temp[7].wins}\n"
                                            f"9: {temp[8].name} - {temp[8].wins}\n"
                                            f"10: {temp[9].name} - {temp[9].wins}`")

@bot.tree.command(name="top10losses", description="Check the top 10 players with the most losses")
async def top10losses(interaction: discord.Interaction):
    global registeredPlayers
    temp = []
    temp = sorted(registeredPlayers, key=lambda Player: Player.losses, reverse=True)
    await interaction.response.send_message(f"`1: {temp[0].name} - {temp[0].losses}\n"
                                            f"2: {temp[1].name} - {temp[1].losses}\n"
                                            f"3: {temp[2].name} - {temp[2].losses}\n"
                                            f"4: {temp[3].name} - {temp[3].losses}\n"
                                            f"5: {temp[4].name} - {temp[4].losses}\n"
                                            f"6: {temp[5].name} - {temp[5].losses}\n"
                                            f"7: {temp[6].name} - {temp[6].losses}\n"
                                            f"8: {temp[7].name} - {temp[7].losses}\n"
                                            f"9: {temp[8].name} - {temp[8].losses}\n"
                                            f"10: {temp[9].name} - {temp[9].losses}`")

@bot.tree.command(name="top10wlr", description="Check the top 10 Win/Loss ratings")
async def top10wlr(interaction: discord.Interaction):
    global registeredPlayers
    temp = []
    temp = sorted(registeredPlayers, key=lambda Player: Player.wlr, reverse=True)
    await interaction.response.send_message(f"`1: {temp[0].name} - {temp[0].wlr}%\n"
                                            f"2: {temp[1].name} - {temp[1].wlr}%\n"
                                            f"3: {temp[2].name} - {temp[2].wlr}%\n"
                                            f"4: {temp[3].name} - {temp[3].wlr}%\n"
                                            f"5: {temp[4].name} - {temp[4].wlr}%\n"
                                            f"6: {temp[5].name} - {temp[5].wlr}%\n"
                                            f"7: {temp[6].name} - {temp[6].wlr}%\n"
                                            f"8: {temp[7].name} - {temp[7].wlr}%\n"
                                            f"9: {temp[8].name} - {temp[8].wlr}%\n"
                                            f"10: {temp[9].name} - {temp[9].wlr}%`")

@bot.tree.command(name="top10gp", description="Check the top 10 players with the most games played")
async def top10gp(interaction: discord.Interaction):
    global registeredPlayers
    temp = []
    temp = sorted(registeredPlayers, key=lambda Player: Player.gp, reverse=True)
    await interaction.response.send_message(f"`1: {temp[0].name} - {temp[0].gp}\n"
                                            f"2: {temp[1].name} - {temp[1].gp}\n"
                                            f"3: {temp[2].name} - {temp[2].gp}\n"
                                            f"4: {temp[3].name} - {temp[3].gp}\n"
                                            f"5: {temp[4].name} - {temp[4].gp}\n"
                                            f"6: {temp[5].name} - {temp[5].gp}\n"
                                            f"7: {temp[6].name} - {temp[6].gp}\n"
                                            f"8: {temp[7].name} - {temp[7].gp}\n"
                                            f"9: {temp[8].name} - {temp[8].gp}\n"
                                            f"10: {temp[9].name} - {temp[9].gp}`")

@bot.tree.command(name="top10kpr", description="Check the top 10 players with the best kpr")
async def top10kpr(interaction: discord.Interaction):
    global registeredPlayers
    temp = []
    temp = sorted(registeredPlayers, key=lambda Player: Player.kpr, reverse=True)
    await interaction.response.send_message(f"`1: {temp[0].name} - {temp[0].kpr}\n"
                                            f"2: {temp[1].name} - {temp[1].kpr}\n"
                                            f"3: {temp[2].name} - {temp[2].kpr}\n"
                                            f"4: {temp[3].name} - {temp[3].kpr}\n"
                                            f"5: {temp[4].name} - {temp[4].kpr}\n"
                                            f"6: {temp[5].name} - {temp[5].kpr}\n"
                                            f"7: {temp[6].name} - {temp[6].kpr}\n"
                                            f"8: {temp[7].name} - {temp[7].kpr}\n"
                                            f"9: {temp[8].name} - {temp[8].kpr}\n"
                                            f"10: {temp[9].name} - {temp[9].kpr}`")

@bot.tree.command(name="top10rp", description="Check the top 10 players with the most rounds played")
async def top10rp(interaction: discord.Interaction):
    global registeredPlayers
    temp = []
    temp = sorted(registeredPlayers, key=lambda Player: Player.rp, reverse=True)
    await interaction.response.send_message(f"`1: {temp[0].name} - {temp[0].rp}\n"
                                            f"2: {temp[1].name} - {temp[1].rp}\n"
                                            f"3: {temp[2].name} - {temp[2].rp}\n"
                                            f"4: {temp[3].name} - {temp[3].rp}\n"
                                            f"5: {temp[4].name} - {temp[4].rp}\n"
                                            f"6: {temp[5].name} - {temp[5].rp}\n"
                                            f"7: {temp[6].name} - {temp[6].rp}\n"
                                            f"8: {temp[7].name} - {temp[7].rp}\n"
                                            f"9: {temp[8].name} - {temp[8].rp}\n"
                                            f"10: {temp[9].name} - {temp[9].rp}`")

#Displays how often the maps from the Ranked CvC map pool have been played
@bot.tree.command(name="maps", description="Check how often certain maps are played")
async def maps(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Alleyway: {alleyInt}\nAtomic: {atomInt}\nMirage: {mirageInt}\nCarrier: {carrierInt}\nCobblestone: {cobbleInt}\n"
        f"Train: {trainInt}\nOverpass: {opInt}\nOvergrown: {ogInt}\nCache: {cacheInt}\nAncient: {ancientInt}\n"
        f"Sandstorm: {sandInt}\nTemple: {templeInt}")

#Takes the username of every player and puts it on a text file in the directory where the bot is being run
#Params: User must have the "Admin" role to run this command
@bot.tree.command(name="exportusers", description="Generate a list of all registered players to a text file")
@app_commands.checks.has_role("Admin")
async def exportusers(interaction: discord.Interaction):
    #We create a file called "rankedCvCPlayers.txt" and write the name of every user separated by a newline in the file
    file = open("rankedCvCPlayers.txt", "w")
    for x in registeredPlayers:
        file.write(f"{x.name}\n")
    #Once we're done, close the file and send a success message
    file.close()
    await interaction.response.send_message("Users successfully exported")

#Reads a text file that contains a username and then a newline, upon reading the username it registers a player
#Params: Takes a textfile as a string, the text file should be generated by the exportusers command
#Params: User must have the "Admin" role to run this command
@bot.tree.command(name="importusers", description="Import a list of users that will be automatically registered")
@app_commands.describe(textfile="Name of file to import")
@app_commands.checks.has_role("Admin")
async def importusers(ctx, textfile: str):
    file = open(textfile, "r")
    lines = file.readlines()
    for y in lines:
        await registerHelper(ctx, message=y)
    await ctx.response.send_message("Users successfully imported")


#This function behaves identically to the "cvcregister" command, but was created due to how slash commands interact with each other
async def registerHelper(ctx, *, message):
    global registeredPlayers
    name = message.split()
    player = name[-1]
    uuid = get_uuid(player)
    if uuid != "ERROR":
        stats = get_API(uuid)
        try:
            cvc_defusal_wins = stats["player"]["stats"]["MCGO"]["game_wins"]
        except:
            cvc_defusal_wins = 0
        if cvc_defusal_wins == 0:
            return
        for x in registeredPlayers:
            if player.lower() == x.name.lower():
                return
        app = Player(player, 0, 0, 0, 0, 0, len(registeredPlayers) + 1, 1500, 0, 0, 0, 0)
        registeredPlayers.append(app)
        registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
        for i in range(len(registeredPlayers)):
            registeredPlayers[i].rank = i + 1

#This command takes in 10 usernames and sorts them by rating. The top 2 players are the captains
@bot.tree.command(name="captains", description="Check who the captains are (requires 10 names")
async def captains(interaction: discord.Interaction, name1: str, name2: str, name3: str, name4: str, name5: str, name6: str,
                   name7: str, name8: str, name9: str, name10: str):
    global registeredPlayers
    captains = []
    for x in registeredPlayers:
        if name1.lower() == x.name.lower():
            captains.append(x)
        if name2.lower() == x.name.lower():
            captains.append(x)
        if name3.lower() == x.name.lower():
            captains.append(x)
        if name4.lower() == x.name.lower():
            captains.append(x)
        if name5.lower() == x.name.lower():
            captains.append(x)
        if name6.lower() == x.name.lower():
            captains.append(x)
        if name7.lower() == x.name.lower():
            captains.append(x)
        if name8.lower() == x.name.lower():
            captains.append(x)
        if name9.lower() == x.name.lower():
            captains.append(x)
        if name10.lower() == x.name.lower():
            captains.append(x)
    captains = sorted(captains, key=lambda Player: Player.rating, reverse=True)
    await interaction.response.send_message(f"Captains are {captains[0].name} and {captains[1].name}\n")


bot.run(TOKEN)

