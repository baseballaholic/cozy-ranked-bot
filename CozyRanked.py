import discord
import json
import requests
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
bot = commands.Bot(command_prefix= "-")

registeredPlayers = []

class Player(object):
    def __init__(self, name, kills, deaths, wins, losses, rank, rating, gp):
        self.name = name
        self.kills = kills
        self.deaths = deaths
        self.wins = wins
        self.losses = losses
        self.rank = rank
        self.rating = rating
        self.gp = gp

    def __repr__(self):
        return repr((self.name, self.kills, self.deaths, self.wins, self.losses, self.rank, self.rating, self.gp))



def find(list, name):
    for x in list:
        if name == x:
            return x.index

def get_uuid(player):
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{player}")
    try:
        uuid = json.loads(response.text)['id']
        return uuid
    except:
        return 'ERROR'

@bot.event
async def on_ready():
    activity = discord.Game(name="Cozy Ranked!")
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command(pass_context=True)
async def r(ctx,*,message):
    global registeredPlayers
    namearray = message.split()
    player = namearray[-1]
    kd = 0
    wl = 0
    true = 0
    for x in registeredPlayers:
        if player.lower() == x.name.lower():
            true = 1
            if x.deaths != 0:
                kd = round((x.kills/x.deaths), 3)
            if x.losses != 0:
                wl = round((x.wins/x.losses)*100, 3)
            elif x.losses == 0 and x.wins > 0:
                wl = 100
            await ctx.send(f"{x.name} has rank {x.rank} with a rating of {x.rating} with a KDA of {kd}" \
                 f" and a W/L of {x.wins}/{x.losses} ({wl}%)")
    if true == 0:
        await ctx.send("Invalid Player")

@bot.command(pass_context=True)
async def register(ctx,*,message):
    global registeredPlayers
    name = message.split()
    player = name[-1]
    uuid = get_uuid(player)
    dupe = -2
    if uuid != "ERROR":
        for x in registeredPlayers:
            if player.lower() == x.name.lower():
                dupe = 1
        if dupe != 1:
            app = Player(player, 0, 0, 0, 0, len(registeredPlayers)+1, 1500, 0)
            registeredPlayers.append(app)
            await ctx.send(f"{player} has been registered")
        else:
            await ctx.send(f"{player} was already registered")
        registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
        for i in range(len(registeredPlayers)):
            registeredPlayers[i].rank = i + 1
    else:
        await ctx.send("Invalid Player")

@bot.command()
async def lb(ctx):
    global registeredPlayers
    await ctx.send(f"```1. {registeredPlayers[0].name} - {registeredPlayers[0].rating}\n"
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

@bot.command()
async def lb2(ctx):
    global registeredPlayers
    if(len(registeredPlayers) > 80):
        await ctx.send(f"```41. {registeredPlayers[40].name} - {registeredPlayers[40].rating}\n"
                               f"42. {registeredPlayers[41].name} - {registeredPlayers[41].rating}\n"
                               f"43. {registeredPlayers[42].name} - {registeredPlayers[2].rating}\n"
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
        await ctx.send("Not enough players to display leaderboard 2\n")

@bot.command(pass_context=True)
@commands.has_permissions(add_reactions=True)
async def delete(ctx,*,message):
    global registeredPlayers
    name = message.split()
    player = name[-1]
    for x in registeredPlayers:
        if player.lower() == x.name.lower():
            registeredPlayers.remove(x)
            await ctx.send(f"{player} has been removed")
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1


@bot.command(pass_context=True)
@commands.has_permissions(add_reactions=True)
async def addstats(ctx,*,message):
    global registeredPlayers
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    stats = message.split()
    for y in range(len(stats)):
        if stats[y] == "A":
            a = stats[y + 1]
            if a == "12":
                winner = 0
        if stats[y] == "B":
            b = stats[y + 1]
            if b == "12":
                winner = 1

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

                if (x.wins + x.losses) < 101:
                    formula = x.rating + (int(kd[0]) - int(kd[1]) + ELO)
                else:
                    formula = x.rating + (
                                (int(kd[0]) - int(kd[1]) + ELO) - ((x.kills - x.deaths) + 12 * (x.wins - x.losses)) / (
                                    x.wins + x.losses))

                x.kills += int(kd[0])
                x.deaths += int(kd[1])
                if ELO == 12:
                    x.wins += 1
                    x.gp += 1
                if ELO == -12:
                    x.losses += 1
                    x.gp += 1
                x.rating = formula
    if counter != 10:
        await ctx.send("Warning: Stats were entered with an unregistered player\n"
                       "Please remove these stats, register all players, and then re-enter the stats")
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1

@bot.command(pass_context=True)
@commands.has_permissions(add_reactions=True)
async def removestats(ctx,*,message):
    global registeredPlayers
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    stats = message.split()
    for y in range(len(stats)):
        if stats[y] == "A":
            a = stats[y + 1]
            if a == "12":
                winner = 0
        if stats[y] == "B":
            b = stats[y + 1]
            if b == "12":
                winner = 1

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

                if (x.wins + x.losses) < 101:
                    formula = x.rating - (int(kd[0]) - int(kd[1]) + ELO)
                else:
                    formula = x.rating - (
                                (int(kd[0]) - int(kd[1]) + ELO) - ((x.kills - x.deaths) + 12 * (x.wins - x.losses)) / (
                                    x.wins + x.losses))

                x.kills -= int(kd[0])
                x.deaths -= int(kd[1])
                if ELO == 12:
                    x.wins -= 1
                    x.gp -= 1
                if ELO == -12:
                    x.losses -= 1
                    x.gp -= 1
                x.rating = formula
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1

@bot.command(pass_context=True)
@commands.has_permissions(add_reactions=True)
async def changename(ctx,*,message):
    global registeredPlayers
    names = message.split()
    name1 = names[-2]
    name2 = names[-1]
    true = 0
    for x in registeredPlayers:
        if name1 == x.name:
            x.name = name2
            true = 1
            await ctx.send("Name Changed")

    if true == 0:
        await ctx.send("Error: Failed to change name")

@bot.command(pass_context=True)
@commands.has_permissions(send_tts_messages=True)
async def set(ctx,*,message):
    global registeredPlayers
    names = message.split()
    name = names[0]
    kills = int(names[1])
    deaths = int(names[2])
    wins = int(names[3])
    losses = int(names[4])
    rank = int(names[5])
    rating = int(names[6])
    gp = int(names[7])
    for x in registeredPlayers:
        if name == x.name:
            x.kills = kills
            x.deaths = deaths
            x.wins = wins
            x.losses = losses
            x.rank = rank
            x.rating = rating
            x.gp = gp

@bot.command(pass_context=True)
@commands.has_permissions(add_reactions=True)
async def botban(ctx):
    global registeredPlayers
    await ctx.send(
        "Warning: This does not take into account if it has been 5 games since a players last bot ban\n")
    for x in registeredPlayers:
        if (x.deaths > 0):
            if (x.gp) >= 10 and (x.kills / x.deaths) < 0.5 and (x.wins / x.losses) < 0.5:
                await ctx.send(
                    f"{x.name} needs a bot ban (KDR: {round((x.kills / x.deaths), 3)}) and WL: {round((x.wins / x.losses) * 100, 3)}\n")
            elif (x.gp) >= 5 and (x.kills / x.deaths) < 0.4:
                await ctx.send(
                    f"{x.name} needs a bot ban (KDR: {round((x.kills / x.deaths), 3)}) and WL: {round((x.wins / x.losses) * 100, 3)}\n")

@bot.command(pass_context=True)
@commands.has_permissions(send_tts_messages=True)
async def resetseasonabcdefghijklmnopqrstuvwxyz(ctx):
    global registeredPlayers
    for i in registeredPlayers:
        i.kills = 0
        i.deaths = 0
        i.wins = 0
        i.losses = 0
        i.rating = 1500
        i.gp = 0
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1

@bot.command(pass_context=True)
@commands.has_permissions(add_reactions=True)
async def minus20(ctx,*,message):
    global registeredPlayers
    arr = message.split()
    name = arr[-1]
    for x in registeredPlayers:
        if name == x.name:
            x.rating-=20
            await ctx.send(f"20 elo has been removed from {x.name}")

@bot.command(pass_context=True)
@commands.has_permissions(add_reactions=True)
async def addstatsnoeloloss(ctx,*,message):
    global registeredPlayers
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    stats = message.split()
    for y in range(len(stats)):
        if stats[y] == "A":
            a = stats[y + 1]
            if a == "12":
                winner = 0
        if stats[y] == "B":
            b = stats[y + 1]
            if b == "12":
                winner = 1

    for i in range(len(stats)):
        for x in registeredPlayers:
            if stats[i] == x.name:
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

                if (x.wins + x.losses) < 101:
                    formula = x.rating + (int(kd[0]) - int(kd[1]) + ELO)
                else:
                    formula = x.rating + (
                            (int(kd[0]) - int(kd[1]) + ELO) - ((x.kills - x.deaths) + 12 * (x.wins - x.losses)) / (
                            x.wins + x.losses))
                if(ELO == 12):
                    x.kills += int(kd[0])
                    x.deaths += int(kd[1])
                    if ELO == 12:
                        x.wins += 1
                        x.gp += 1
                    if ELO == -12:
                        x.gp += 1
                        x.losses += 1
                    x.rating = formula
    if counter != 10:
        await ctx.send("Warning: Stats were entered with an unregistered player\n"
                       "Please remove these stats, register all players, and then re-enter the stats")
    registeredPlayers = sorted(registeredPlayers, key=lambda Player: Player.rating, reverse=True)
    for i in range(len(registeredPlayers)):
        registeredPlayers[i].rank = i + 1

@bot.command(pass_context=True)
@commands.has_permissions(send_tts_messages=True)
async def top10kills(ctx):
    global registeredPlayers
    temp = []
    temp = sorted(registeredPlayers, key=lambda Player: Player.kills, reverse=True)
    for i in range(0, 10):
        await ctx.send(f"{i+1}: {temp[i].name} - {temp[i].kills}")

@bot.command(pass_context=True)
@commands.has_permissions(send_tts_messages=True)
async def exportAllUsers(ctx):
    file = open("rankedCvCPlayers.txt", "w")
    for x in registeredPlayers:
        file.write(f"{x.name}\n")
    file.close()
    await ctx.send("Users successfully exported")

@bot.command(pass_context=True)
@commands.has_permissions(send_tts_messages=True)
async def importAllUsers(ctx,*,message):
    file = open(message, "r")
    lines = file.readlines()
    for y in lines:
        await register(ctx, message=y)
    await ctx.send("Users successfully imported")

@bot.command(pass_context=True)
async def captains(ctx,*,message):
    global registeredPlayers
    names = message.split()
    captains = []
    for i in names:
        for x in registeredPlayers:
            if i.lower() == x.name.lower():
                captains.append(i)
                if(len(captains) == 2):
                    await ctx.send(f"Captains are {captains[0]} and {captains[1]}\n")
                    return

bot.run('ODM0NTg2NjY2NjQzMDk1NjEy.YIDDZw.K2kUP3g2cx1Apjv4y78rNhvPjxE')



