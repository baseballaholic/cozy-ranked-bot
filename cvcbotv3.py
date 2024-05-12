import discord
import json
import requests
from discord.ext import commands
from discord import app_commands
from Pagination import Pagination
from datetime import date
import sqlite

bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())
TOKEN = "MTAyNTk2NTQ2MjM1OTY0MjE3Mw.GsX35g.a5fJj4Q0wR_jz75YHwV8UcV0sJJ9A8UKALkm8Q"

database = "test.db"
conn = sqlite.create_connection(database)
# Global Boolean for whether the Audit log is toggled on or off (Currently the Audit Log does not work)
audit = False

# My own API key so I can access the API easily
API_KEY = "8493fb61-c7d7-4959-8fa3-17686d2c1ecc"


class Select(discord.ui.Select):
    def __init__(self, minimum, interaction: discord.Interaction):
        options = [
            discord.SelectOption(label="Kills", description="This is for top 10 kills"),
            discord.SelectOption(label="Deaths", description="This is for top 10 deaths"),
            discord.SelectOption(label="KDR", description="This is the top 10 KDR"),
            discord.SelectOption(label="Wins", description="This is the top 10 Wins"),
            discord.SelectOption(label="Losses", description="This is the top 10 Losses"),
            discord.SelectOption(label="Games Played", description="This is the top 10 Games Played"),
            discord.SelectOption(label="WLR", description="This is the top 10 WLR"),
            discord.SelectOption(label="Rounds Played", description="This is the top 10 Rounds Played"),
            discord.SelectOption(label="KPR", description="This is the top 10 KPR"),
            discord.SelectOption(label="Average Elo", description="This is the top 10 Average Elo/Game")
        ]
        self.minimum = minimum
        self.interaction = interaction
        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        string = ""
        if self.minimum > 0:
            string = f" (min {self.minimum})"
        genlb = generatetop10(self.values[0], self.minimum)
        await interaction.response.edit_message(
            content=f"__**Top 10 {self.values[0]}{string}**__\n```{(''.join(map(str, genlb)))}```")


class SelectView(discord.ui.View):
    def __init__(self, *, timeout=180, minimum, interaction):
        super().__init__(timeout=timeout)
        self.minimum = minimum
        self.interaction = interaction
        self.add_item(Select(self.minimum, self.interaction))

    async def on_timeout(self):
        # remove dropdown on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            emb = discord.Embed(
                description=f"Only the author of the command can perform this action.",
                color=16711680
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False


# Grabs the UUID of a registered user
def get_uuid(player):
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{player}")
    try:
        uuid = json.loads(response.text)['id']
        return uuid
    except:
        return 'ERROR'


# Prepares to make a call to the API
def getinfo(call):
    r = requests.get(call)
    return r.json()


# Returns all of a player's data from the API
def get_API(player):
    data = getinfo(f"https://api.hypixel.net/player?key={API_KEY}&uuid={player}")
    return data


def update_rankings():
    players = sqlite.select_all_players_by_rating(conn)
    rank = 1
    for player in players:
        query = sqlite.update_rankings(conn, player[1], rank)
        if query == "success":
            rank += 1
    return "hooray"


def update_top_20_ids():
    top20 = sqlite.select_all_top_20_by_id(conn)
    top20pm = sqlite.select_all_top_20_pm_by_id(conn)
    top20id = 1
    top20pmid = 1
    for i in top20:
        query = sqlite.update_top20_ids(conn, i[0], top20id)
        if query == "success":
            top20id += 1
    for j in top20pm:
        querypm = sqlite.update_top20pm_ids(conn, j[0], top20pmid)
        if querypm == "success":
            top20pmid += 1
    return "hooray"


def generatetop20kills(start, end):
    top20kills = sqlite.generate_top_20_kills(conn, end)  # id, name, kills, deaths, pm, date
    pm = ""
    for i in range(start, end):
        if top20kills[i][4] > -1:
            pm = "+"
        else:
            pm = ""
        # yield f"{(i+1)}. {top20kills[i][1]} - {top20kills[i][2]}-{top20kills[i][3]} {pm}{top20kills[i][4]} on {top20kills[i][5]}\n"
        yield "{:<3} {:<15} - {:>2}-{:<2} {:<0}{:<3} on {:<15}\n".format(f"{(i + 1)}.", top20kills[i][1],
                                                                         top20kills[i][2], top20kills[i][3], pm,
                                                                         top20kills[i][4], top20kills[i][5])


def generatetop20pm(start, end):
    top20pm = sqlite.generate_top_20_pm(conn, end)  # id, name, kills, deaths, pm, date
    pm = ""
    for i in range(start, end):
        if top20pm[i][4] > -1:
            pm = "+"
        else:
            pm = ""
        # yield f"{(i+1)}. {top20pm[i][1]} - {top20pm[i][2]}-{top20pm[i][3]} {pm}{top20pm[i][4]} on {top20pm[i][5]}\n"
        yield "{:<3} {:<15} - {:>2}-{:<2} {:<0}{:<3} on {:<15}\n".format(f"{(i + 1)}.", top20pm[i][1],
                                                                         top20pm[i][2], top20pm[i][3], pm,
                                                                         top20pm[i][4], top20pm[i][5])


async def removestatshelper(message, date, noeloloss):
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    rounds = 0
    update = 0
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
            if c.lower() == "cobble":
                c = "cobblestone"
            if c.lower() == "ruins":
                c = "ancient"
            times_played = sqlite.get_times_played(conn, c)
            map_query = sqlite.updatemap(conn, c, times_played - 1)
            if map_query == "error":
                print("Map not found, try again (use /maps for correct spellings)")
                return

    for i in range(len(stats)):
        valid = sqlite.check_valid(conn, stats[i])
        if valid == "success":
            user = stats[i]
            kills, deaths, rating, wins, losses, gp, rp = sqlite.get_add_stats(conn, user)
            if counter < 5:
                teamOne.append(user)
                counter += 1
            else:
                teamTwo.append(user)
                counter += 1
            if user in teamOne and winner == 0:
                ELO = 12
            elif user in teamOne and winner == 1:
                ELO = -12
            elif user in teamTwo and winner == 0:
                ELO = -12
            elif user in teamTwo and winner == 1:
                ELO = 12
            kd = stats[i + 1].split("-")

            if sqlite.get_gp(conn, user) < 151:
                formula = rating - (int(kd[0]) - int(kd[1]) + ELO)
            else:
                formula = rating - (
                        (int(kd[0]) - int(kd[1]) + ELO) - (((kills - int(kd[0])) - (deaths - int(kd[1])))
                                                           + 12 * (wins - losses - 1)) / (gp - 1))
            if ELO == 12 or (ELO == -12 and noeloloss == "False"):
                validtop20, top20id = sqlite.check_valid_top_20(conn, kills, user, deaths)
                validtop20pm, top20pmid = sqlite.check_valid_top_20_pm(conn, kills, user, deaths)
                if validtop20 == "success":
                    if sqlite.delete_top_20(conn, top20id) == "success":
                        update = 1
                if validtop20pm == "success":
                    if sqlite.delete_top_20_pm(conn, top20pmid) == "success":
                        update = 1
                sqlite.update_kills(conn, ((kills - int(kd[0])), user))
                sqlite.update_deaths(conn, ((deaths - int(kd[1])), user))
                sqlite.update_rp(conn, ((rp - rounds), user))
                sqlite.update_gp(conn, ((gp - 1), user))
                if sqlite.get_deaths(conn, user) == 0:
                    sqlite.update_kdr(conn, (0, user))
                elif sqlite.get_deaths(conn, user) > 0:
                    sqlite.update_kdr(conn,
                                      ((round(sqlite.get_kills(conn, user) / sqlite.get_deaths(conn, user), 3)), user))
                if sqlite.get_rp(conn, user) > 0:
                    sqlite.update_kpr(conn, ((round(sqlite.get_kills(conn, user) / sqlite.get_rp(conn, user), 3)), user))
                if ELO == 12:
                    sqlite.update_wins(conn, ((wins - 1), user))
                if ELO == -12:
                    sqlite.update_losses(conn, ((losses - 1), user))
                if sqlite.get_gp(conn, user) != 0:
                    sqlite.update_wlr(conn,
                                      ((round((sqlite.get_wins(conn, user) / sqlite.get_gp(conn, user)) * 100, 3)), user))
                else:
                    sqlite.update_wlr(conn, (0, user))
                sqlite.update_rating(conn, ((round(formula, 3)), user))
                if sqlite.get_gp(conn, user) > 0:
                    sqlite.update_avgelo(conn, (
                    (round((sqlite.get_rating(conn, user) - 1500) / sqlite.get_gp(conn, user), 3)), user))
                else:
                    sqlite.update_avgelo(conn, (0, user))

    update_rankings()
    if update == 1:
        update_top_20_ids()
        await posttop20(sqlite.total_top_20(conn), sqlite.total_top_20_pm(conn))
    return


@bot.event
async def on_ready():
    activity = discord.Game(name="Cozy Ranked!")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print('We have logged in as {0.user}'.format(bot))
    #guild = discord.Object(id=525020775850311690)
    guild = discord.Object(id=881008769511854091)
    try:
        #bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


# Error Handling
@bot.tree.error
async def on_application_command_error(interaction, error):
    # If the user generates the error that they were missing the required role for a command
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("You do not have the specific role to run this command", ephemeral=True)
    elif isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("You do not have the specific role to run this command",
                                                ephemeral=True)
    else:
        raise error


@bot.tree.command(name="findchannel", description="Print out the channel the command was sent from")
@app_commands.checks.has_any_role(525025520975609866, 827513306788266024, 1059228479163469945)
async def findchannel(interaction: discord.Interaction):
    channelID = interaction.user.voice.channel.id
    members = interaction.user.voice.channel.members
    memberID = []
    for i in members:
        memberID.append(i.id)
    await interaction.response.send_message(f"Channel ID: {channelID}\n"
                                            f"Channel Members: {memberID}\n"
                                            f"Interaction User ID: {interaction.user.id}")


@bot.tree.command(name="help", description="Check out the commands you can use")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message("Help: Displays the command you are currently using\n"
                                            "r (username): Check a player's stats\n"
                                            "cvcregister (username): Register a player for Ranked CvC\n"
                                            "lb: Check the first page of the Ranked CvC Leaderboards\n"
                                            "Captains: Displays the top 4 captain candidates in a Ranked lobby\n"
                                            "maps: Check how often certain maps are played in Ranked CvC\n"
                                            "top10: Check the top 10 of different statistical categories for Ranked CvC",
                                            ephemeral=True)


# Command to check a player's stats
# Param: Takes a string as a username
@bot.tree.command(name="r", description="Check a player's stats")
@app_commands.describe(username="Check a users stats")
async def r(interaction: discord.Interaction, username: str = None):
    did = None
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /r {username}")
    if (username == None):
        did = str(interaction.user.id)
    query = sqlite.r(conn, username, did)
    if query == "error":
        await interaction.response.send_message("User does not exist")
        return
    name, rank, rating, kd, wins, losses, wl, kpr = query
    await interaction.response.send_message(
        f"{name} has rank {rank} with a rating of {rating} with a KDA of {kd}"
        f", a W/L of {wins}/{losses} ({wl}%), and a KPR of {kpr}")


# Command to register a user for Ranked CvC
# Param: Takes a username as a string
@bot.tree.command(name="cvcregister", description="Register a player")
@app_commands.describe(username="Register a player")
async def cvcregister(interaction: discord.Interaction, username: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /cvcregister {username}")
    player = username
    # Grab the UUID
    uuid = get_uuid(player)
    # Set a variable as a flag for if the user is already registered
    dupe = -2

    # If the UUID is valid
    if uuid != "ERROR":
        # Grab the player's API
        stats = get_API(uuid)
        try:
            # If the user has generated the API endpoint for winning a game of defusal, then return the wins they have
            cvc_defusal_wins = stats["player"]["stats"]["MCGO"]["game_wins"]
        except:
            # Otherwise, set their wins to 0
            cvc_defusal_wins = 0

        if cvc_defusal_wins == 0:
            # If they don't have enough wins they can't register
            await interaction.response.send_message("Invalid Player")
            return

        did = str(interaction.user.id)
        query = sqlite.register(conn, player, did)
        if query == "error":
            await interaction.response.send_message("User is already registered")
            return
        if query == "success":
            confirm = update_rankings()  # Update rankings
            await interaction.response.send_message(f"{player} has been registered")
    else:
        # If the UUID wasn't valid then the account doesn't exist
        await interaction.response.send_message("Invalid Player")


# Function deletes a user from the data, opposite of registering a player
# Params: Takes a username as a string
@bot.tree.command(name="delete", description="Delete a registered player")
@app_commands.describe(username="Delete a player")
@app_commands.checks.has_any_role(525025520975609866, 827513306788266024, 1059228479163469945)
async def delete(interaction: discord.Interaction, username: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /delete {username}")
    player = username
    query = sqlite.delete(conn, player)
    if query == "error":
        await interaction.response.send_message("User does not exist")
    if query == "success":
        confirm = update_rankings()
        await interaction.response.send_message(f"{username} has been deleted")
        if confirm == "hooray":
            await interaction.followup.send("Rankings have been updated")
    return


@bot.tree.command(name="forceregister", description="Forcefully register a user")
@app_commands.describe(username="Force Register a user", id="Discord ID of the user")
@app_commands.checks.has_any_role(525025520975609866, 827513306788266024, 1059228479163469945)
async def forceregister(interaction: discord.Interaction, username: str, id: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /forceregister {username} {id}")
    query = sqlite.forceregister(conn, username, id)
    if query == "error":
        await interaction.response.send_message("User already exists with this name or ID")
    if query == "success":
        confirm = update_rankings()  # Update rankings
        await interaction.response.send_message(f"{username} has been registered")
    return


@bot.tree.command(name="lb", description="Displays the Leaderboard of Ranked CvC")
async def lb(interaction: discord.Interaction, player: str = None):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /lb {player}\n")
    rank = 0
    index = 1
    if player != None:
        rank = sqlite.lb(conn, player)
        if rank == "error":
            await interaction.response.send_message("User does not exist")
            return
        rank = rank[0]
        index = int(rank / 40) + 1

    async def get_page(page: int, first: bool):
        emb = discord.Embed(title="Ranked CvC Leaderboard", description="")
        offset = (page - 1) * 40
        if rank != 0 and first == True:
            genlb = generatecustomlb(rank - 20, rank + 19, player)
        else:
            genlb = generatelb(offset, offset + 39)
        emb.description += (f"```{(''.join(map(str, genlb)))}```")
        emb.set_author(name=f"Requested by {interaction.user}")
        n = Pagination.compute_total_pages(sqlite.total_players(conn), 40)
        emb.set_footer(text=f"Page {page} from {n}")
        return emb, n

    await Pagination(interaction, get_page, index).navegate()


def generatecustomlb(start, end, player):
    query = sqlite.generatecustomlb(conn, start + 19)  # rank, rating, name
    total = sqlite.total_players(conn)
    for i in range(0, 40):
        if 0 <= i < len(query):
            if player.lower() == query[i][2].lower():
                yield f" >>> {query[i][0]}. {query[i][2]} - {query[i][1]}\n"
            else:
                yield f"{query[i][0]}. {query[i][2]} - {query[i][1]}\n"


def generatelb(start, end):
    query = sqlite.generatelb(conn, start, end + 1)  # rank, name, rating
    for i in range(0, len(query)):
        if 0 <= i < sqlite.total_players(conn):
            yield f"{query[i][0]}. {query[i][1]} - {query[i][2]}\n"


# This function parses a text file to add to and update player statistics
# Params: Takes a text file as a string, the text file must be one produced from Podcrash using /pdc exportstats
# Params: User must have the "Ranked Staff" role, otherwise the command will not work
@bot.tree.command(name="addstats", description="Add stats to the bot")
@app_commands.describe(stats="Add the stats",
                       noeloloss="Whether or not the game will be no elo loss (True or False, default is False)")
@app_commands.checks.has_any_role(525025520975609866, 827513306788266024, 1059228479163469945)
async def addstats(interaction: discord.Interaction, stats: str, noeloloss: str = "False"):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /addstats {stats} \nnoeloloss: {noeloloss}")
    try:
        await interaction.response.defer()
    except discord.errors.HTTPException as e:
        print(e)
        if e == "429":
            await interaction.response.defer()
            # Create 2 Arrays so I can separate the players into 2 teams
    teamOne = []
    teamTwo = []
    # Counter is updated to make sure that the function found 10 players, if not it disregards the stats because there must have been a mistake
    counter = 0
    # If winner is 0 then team A won, if winner is 1 then team B won
    winner = 2
    # Rounds keeps track of how many rounds were played that game
    rounds = 0
    # Split the text file into an array where each index is one word
    stat = stats.split()
    # Var to let us know whether to update the top 20 scores or not
    update = 0
    sent = 0
    time = date.today()
    today = time.strftime("%B %d")
    eloloss = ""
    if noeloloss.lower() == "true":
        eloloss = "(No Elo Loss)"
    for y in range(len(stat)):

        # If we find "A" we know the amount of rounds A team won is the next string
        if stat[y] == "A":
            a = stat[y + 1]
            # Add the amount of rounds A won to the total number of rounds
            rounds += int(a)
            # If A is 12 then we know team A won the game so we declare them the winner
            if a == "12":
                winner = 0

        # If we find "B" we know the amount of rounds A team won is the next string
        if stat[y] == "B":
            b = stat[y + 1]
            # Add the amount of rounds B won to the total number of rounds
            rounds += int(b)
            # If B is 12 then we know team B won the game so we declare them the winner
            if b == "12":
                winner = 1
        # If we find the word "Crims", we know in 2 words from now it will be the map
        if stat[y] == "vs":
            if stat[y + 1] == "Crims":
                # Compare strings to see if the map matches, if it does increase the amount it's been played by 1
                c = stat[y + 3]
                if c.lower() == "cobble":
                    c = "cobblestone"
                if c.lower() == "ruins":
                    c = "ancient"
                times_played = sqlite.get_times_played(conn, c)
                map_query = sqlite.updatemap(conn, c, times_played + 1)
                if map_query == "error":
                    # If we couldn't find the maps, let them know (normally there will be a spelling issue as map name is manually added to the text)
                    try:
                        await interaction.response.send_message(
                            "Map not found, try again (use /maps for correct spellings)")
                    except discord.InteractionResponded:
                        await interaction.followup.send(
                            "Map not found, try again (use /maps for correct spellings)")
                    return
            else:
                try:
                    await interaction.response.send_message(
                        "Unable to locate map, please check for typos and add stats again")
                    return
                except discord.InteractionResponded:
                    await interaction.followup.send(
                        "Unable to locate map, please check for typos and add stats again")
                    return
    for i in range(len(stat)):
        valid = sqlite.check_valid(conn, stat[i])
        if valid == "success":
            user = stat[i]
            kills, deaths, rating, wins, losses, gp, rp = sqlite.get_add_stats(conn, user)
            # Iterate until we find a username, the first 5 usernames go to Team A, the last 5 usernames go to Team B
            if counter < 5:
                teamOne.append(user)
                counter += 1
            else:
                teamTwo.append(user)
                counter += 1
            # If the user is in team A and they won, they gain 12 ELO
            if user in teamOne and winner == 0:
                ELO = 12
            # If the user is in team A and they lost, they lose 12 ELO
            elif user in teamOne and winner == 1:
                ELO = -12
            # If the user is in team B and they won, they gain 12 ELO
            elif user in teamTwo and winner == 0:
                ELO = -12
            # If the user is in team B and they lost, they lose 12 ELO
            elif user in teamTwo and winner == 1:
                ELO = 12
            # kd is an array with the kills and deaths (ex: [17, 14])
            kd = stat[i + 1].split("-")
            try:
                pm = int(stat[i + 2])  # Plus Minus
            except ValueError:
                pm = 0
                await interaction.followup.send(f"+/- not correct for user {user}, please fix issue and remove stats")
            if pm != 0:
                pm = str(stat[i + 2])

            # If the user has played less than 100 games, the formula is different
            if gp < 150:
                # Elo gained in game: previousELO + ((kills - deaths) +/- 12) (depending on win or lose)
                formula = rating + (int(kd[0]) - int(kd[1]) + ELO)
            else:
                # outcome: previousELO + ((elo gained in game) - (expected performance))
                # expected performance: ((total kills - total deaths) + 12*(total wins - total losses))/games played
                formula = rating + (
                        (int(kd[0]) - int(kd[1]) + ELO) - ((kills - deaths)
                                                           + 12 * (wins - losses)) / gp)
            if ELO == 12 or (ELO == -12 and noeloloss == "False"):
                # Update this users kills, deaths, kdr, rounds played, games played
                if sqlite.total_top_20(conn) < 20 or (int(kd[0]) > sqlite.lowest_top_20_kills(conn)):
                    try:
                        top_20_id = sqlite.total_top_20(conn) + 1
                        score = (top_20_id, user, int(kd[0]), int(kd[1]), int(pm), today)
                        sqlite.create_top_20(conn, score)
                        update = 1
                    except ValueError:
                        if sent != 2:
                            await interaction.followup.send(f"Error updating top 20 kills")
                            sent = 2
                if sqlite.total_top_20_pm(conn) < 20 or (
                        int(pm) > sqlite.lowest_top_20_pm(conn)):  # Plus Minus higher than best kill diff
                    try:
                        top_20_pmid = sqlite.total_top_20_pm(conn) + 1
                        score = (top_20_pmid, user, int(kd[0]), int(kd[1]), int(pm), today)
                        sqlite.create_top_20_pm(conn, score)
                        update = 1
                    except:
                        if sent != 1:
                            await interaction.followup.send(f"Error updating top 20 kd")
                        sent = 1
                sqlite.update_kills(conn, ((kills + int(kd[0])), user.lower()))
                sqlite.update_deaths(conn, ((deaths + int(kd[1])), user.lower()))
                if sqlite.get_deaths(conn, user) != 0:
                    sqlite.update_kdr(conn, (
                    (round(sqlite.get_kills(conn, user) / sqlite.get_deaths(conn, user), 3)), user.lower()))
                else:
                    sqlite.update_kdr(conn, (0, user.lower()))
                sqlite.update_rp(conn, ((rp + rounds), user.lower()))
                sqlite.update_gp(conn, ((gp + 1), user.lower()))
                # Avoid divide by 0 errors to set the kills per round
                if sqlite.get_rp(conn, user) > 0:
                    sqlite.update_kpr(conn, (
                    (round(sqlite.get_kills(conn, user) / sqlite.get_rp(conn, user), 3)), user.lower()))
                else:
                    sqlite.update_kpr(conn, (0, user.lower()))
                # If they gained 12 ELO they won so increase their wins by 1, otherwise increase losses by 1
                if ELO == 12:
                    sqlite.update_wins(conn, (wins + 1, user.lower()))
                if ELO == -12:
                    sqlite.update_losses(conn, (losses + 1, user.lower()))
                # Update the win loss rating and update their current rating
                if sqlite.get_gp(conn, user) > 0:
                    sqlite.update_wlr(conn, (
                    (round((sqlite.get_wins(conn, user) / sqlite.get_gp(conn, user)) * 100, 3)), user.lower()))
                else:
                    sqlite.update_wlr(conn, (0, user.lower()))
                sqlite.update_rating(conn, (round(formula, 3), user.lower()))
                sqlite.update_avgelo(conn, (
                round((sqlite.get_rating(conn, user) - 1500) / sqlite.get_gp(conn, user), 3), user.lower()))
    if counter != 10:
        # If we didn't iterate through 10 users, automatically remove the stats that were just input and return
        await removestatshelper(message=stat, date=today, noeloloss=noeloloss)
        await interaction.followup.send("Warning: Stats were entered with an unregistered player\n"
                                        "Stats were automatically removed, register all players, and then re-enter the stats")
        return
    # If everything went right, sort the list by rating and sort ranks
    confirm = update_rankings()
    if update == 1:
        await posttop20(sqlite.total_top_20(conn), sqlite.total_top_20_pm(conn))
    try:
        await interaction.response.send_message(f"Stats Added! {eloloss}")
    except discord.InteractionResponded:
        await interaction.followup.send(f"Stats Added {eloloss}")


async def posttop20(lengthkills, lengthkd):
    endkills = 20
    endkd = 20
    if lengthkills < 20:
        endkills = lengthkills
    if lengthkd < 20:
        endkd = lengthkd
    top20kills = generatetop20kills(0, endkills)
    top20kd = generatetop20pm(0, endkd)
    channel20 = bot.get_channel(1102805295094312990)
    headers = {
        'authorization': 'MTgzNjQwNjQ2ODM2NDIwNjA4.G2R6by.giboTumIvZll2hu4o6dnOobX7cD1_aNDhXoCvU'
    }

    r = requests.get(f'https://discord.com/api/v9/channels/{int(1102805295094312990)}/messages', headers=headers)

    jsonn = json.loads(r.text)
    count = 0
    for value in jsonn:
        message = await channel20.fetch_message(value['id'])
        if count == 1:
            await message.edit(content=f"```Top 20 Kills\n\n{(''.join(map(str, top20kills)))}```")
        if count == 0:
            await message.edit(content=f"```Top 20 Differential\n\n{(''.join(map(str, top20kd)))}```")
        count += 1


# This command goes through our list of players and sets everyones stats to the default
# This would be used at the start of the season in the event we did not need to take the bot down for updates (very rare)
# Params: User must have the "Admin" role
@bot.tree.command(name="resetseasonrankedcvc", description="Resets the season")
@app_commands.checks.has_any_role(525025520975609866, 1059228479163469945)
async def resetseasonrankedcvc(interaction: discord.Interaction):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} for some reason, used /resetseasonrankedcvc")
    print(sqlite.reset_season_players(conn))
    print(sqlite.reset_season_maps(conn))
    print(sqlite.reset_season_top_20(conn))
    print(sqlite.reset_season_top_20_pm(conn))
    update_rankings()
    await interaction.response.send_message("Oh boy, hope you meant to do that")


# This function parses a text file to subtract from and update player statistics
# Params: Takes a text file as a string, the text file must be one produced from Podcrash using /pdc exportstats
# Params: User must have the "Ranked Staff" role, otherwise the command will not work
# Note: The code comments are the exact same as the previous function but instead of adding we are subtracting
@bot.tree.command(name="removestats", description="Remove stats from the bot")
@app_commands.describe(stats="Remove the stats", noeloloss="Put 'True' if the game should be no elo loss (Defaults to 'False')")
@app_commands.checks.has_any_role(525025520975609866, 827513306788266024, 1059228479163469945)
async def removestats(interaction: discord.Interaction, stats: str, noeloloss: str = "False"):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /removestats {stats}")
    try:
        await interaction.response.defer()
    except discord.errors.HTTPException as e:
        print(e)
        if e == "429":
            await interaction.response.defer()
    teamOne = []
    teamTwo = []
    counter = 0
    winner = 2
    rounds = 0
    update = 0
    stat = stats.split()
    eloloss = ""
    if noeloloss.lower() == "true":
        eloloss = "(No Elo Loss)"
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
            if c.lower() == "cobble":
                c = "cobblestone"
            if c.lower() == "ruins":
                c = "ancient"
            times_played = sqlite.get_times_played(conn, c)
            map_query = sqlite.updatemap(conn, c, times_played - 1)
            if map_query == "error":
                print("Map not found, try again (use /maps for correct spellings)")
                return

    for i in range(len(stat)):
        valid = sqlite.check_valid(conn, stat[i])
        if valid == "success":
            user = stat[i]
            kills, deaths, rating, wins, losses, gp, rp = sqlite.get_add_stats(conn, user)
            if counter < 5:
                teamOne.append(user)
                counter += 1
            else:
                teamTwo.append(user)
                counter += 1
            if user in teamOne and winner == 0:
                ELO = 12
            elif user in teamOne and winner == 1:
                ELO = -12
            elif user in teamTwo and winner == 0:
                ELO = -12
            elif user in teamTwo and winner == 1:
                ELO = 12
            kd = stat[i + 1].split("-")

            if gp < 151:
                formula = rating - (int(kd[0]) - int(kd[1]) + ELO)
            else:
                formula = rating - (
                        (int(kd[0]) - int(kd[1]) + ELO) - (
                            ((kills - int(kd[0])) - (deaths - int(kd[1]))) + 12 * (wins - losses - 1)) / (
                                gp - 1))
            if ELO == 12 or (ELO == -12 and noeloloss == "False"):
                validtop20, top20id = sqlite.check_valid_top_20(conn, int(kd[0]), user, int(kd[1]))
                validtop20pm, top20pmid = sqlite.check_valid_top_20_pm(conn, int(kd[0]), user, int(kd[1]))
                if validtop20 == "success":
                    if sqlite.delete_top_20(conn, top20id) == "success":
                        update = 1
                if validtop20pm == "success":
                    if sqlite.delete_top_20_pm(conn, top20pmid) == "success":
                        update = 1
                sqlite.update_kills(conn, ((kills - int(kd[0])), user.lower()))
                sqlite.update_deaths(conn, ((deaths - int(kd[1])), user.lower()))
                sqlite.update_rp(conn, ((rp - rounds), user.lower()))
                sqlite.update_gp(conn, ((gp - 1), user.lower()))
                if sqlite.get_deaths(conn, user.lower()) == 0:
                    sqlite.update_kdr(conn, (0, user.lower()))
                elif sqlite.get_deaths(conn, user.lower()) > 0:
                    sqlite.update_kdr(conn,
                                      ((round(sqlite.get_kills(conn, user.lower()) / sqlite.get_deaths(conn, user.lower()), 3)), user.lower()))
                if sqlite.get_rp(conn, user.lower()) > 0:
                    sqlite.update_kpr(conn, ((round(sqlite.get_kills(conn, user.lower()) / sqlite.get_rp(conn, user.lower()), 3)), user.lower()))
                if ELO == 12:
                    sqlite.update_wins(conn, ((wins - 1), user.lower()))
                if ELO == -12:
                    sqlite.update_losses(conn, ((losses - 1), user.lower()))
                if sqlite.get_gp(conn, user.lower()) != 0:
                    sqlite.update_wlr(conn,
                                      ((round((sqlite.get_wins(conn, user.lower()) / sqlite.get_gp(conn, user.lower())) * 100, 3)), user.lower()))
                else:
                    sqlite.update_wlr(conn, (0, user.lower()))
                sqlite.update_rating(conn, ((round(formula, 3)), user.lower()))
                if sqlite.get_gp(conn, user.lower()) > 0:
                    sqlite.update_avgelo(conn, (
                        (round((sqlite.get_rating(conn, user.lower()) - 1500) / sqlite.get_gp(conn, user.lower()), 3)), user.lower()))
                else:
                    sqlite.update_avgelo(conn, (0, user.lower()))
    update_rankings()
    if update == 1:
        update_top_20_ids()
        await posttop20(sqlite.total_top_20(conn), sqlite.total_top_20_pm(conn))
    try:
        await interaction.response.send_message(f"Stats Removed! {eloloss}")
    except discord.InteractionResponded:
        await interaction.followup.send(f"Stats Removed {eloloss}")
    return


# Command to change a registered player's username
# Params: Takes a username as a string
# Params: User must have the Ranked Staff role to use this command
@bot.tree.command(name="changename", description="Change the first name to the second")
@app_commands.describe(oldname="Original Username", newname="New Username")
@app_commands.checks.has_any_role(525025520975609866, 827513306788266024, 1059228479163469945)
async def changename(interaction: discord.Interaction, oldname: str, newname: str):
    # Set the old name to name1 and set the new name to name2
    name1 = oldname
    name2 = newname
    # Boolean for if we changed the name successfully
    true = 0
    status = "error"
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /changename {oldname} {newname}")
    if name1.lower() == name2.lower() or (
            sqlite.check_valid(conn, name1) == "success" and sqlite.check_valid(conn, name2) != "success"):
        status = sqlite.change_name(conn, oldname, newname)
    if status == "error":
        await interaction.response.send_message(f"'{newname}' is already in use")
        return
    if status == "success":
        true = 1
        await interaction.response.send_message(f"'{oldname}' changed to '{newname}'")
    if true == 0:
        await interaction.response.send_message("Error: Failed to change name")
    return


# This command manually sets a players stats
# Params: (Read the .describe bit)
# Params: User must have the "Admin" role for this command to work
@bot.tree.command(name="set", description="Manually set a player's stats")
@app_commands.describe(name="Username", kills="Kills", deaths="Deaths", kdr="KDR (float)", wins="Wins", losses="Losses",
                       rank="Rank", rating="Rating",
                       gp="Games Played", wlr="Win/Loss Rating (float)", rp="Rounds Played", kpr="Kills/Round (float)",
                       avgelo="Average Elo (float)")
@app_commands.checks.has_any_role(525025520975609866, 1059228479163469945)
async def set(interaction: discord.Interaction, name: str, kills: int, deaths: int, kdr: float, wins: int, losses: int,
              rank: int, rating: int,
              gp: int, wlr: float, rp: int, kpr: float, avgelo: int):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(
            f"{interaction.user.name} used /set {name} {kills} {deaths} {kdr} {wins} {losses} {rank} {rating} {gp} {wlr} {rp} {kpr}")
    stats = (kills, deaths, kdr, wins, losses, rank, rating, gp, wlr, rp, kpr, avgelo, name.lower())
    status = sqlite.set(conn, stats)
    if status == "success":
        await interaction.response.send_message(f"Set {name}'s stats")
        return
    await interaction.response.send_message("Error: Failed to set stats")


# This command prints out a players stats
# Different from -r as this just prints every stat we collect in a single line, -r doesn't print everything
# Params: Takes in a username as a string
# Params: User must have the "Admin" role to run this command
@bot.tree.command(name="get", description="See all of a player's stats")
@app_commands.describe(name="Username")
@app_commands.checks.has_any_role(525025520975609866, 1059228479163469945)
async def get(interaction: discord.Interaction, name: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /get {name}")
    player = sqlite.get(conn, name)
    if player == "error":
        await interaction.response.send_message("User not found")
        return
    if player != "[]" and player != None:
        await interaction.response.send_message(
            f"Username: {player[1]}, Kills: {player[2]}, Deaths: {player[3]}, KDR: {player[4]}, "
            f"Wins: {player[5]}, Losses: {player[6]}, Rank: {player[7]}, Rating: {player[8]}, "
            f"Games Played: {player[9]}, WLR: {player[10]}%, Rounds Played: {player[11]}, KPR: {player[12]}, "
            f"Average Elo: {player[13]}, ID: {player[0]}")
        return
    await interaction.response.send_message("Unknown Error has occurred")
    return


@bot.tree.command(name="top10", description="Brings up the menu to check the top 10 of respective categories")
async def top10(interaction: discord.Interaction, minimum: int = 0):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /top10")
    string = ""
    if minimum > 0:
        string = f" (Min {minimum})"
    await interaction.response.send_message(f"**Top 10 Menu{string}**",
                                            view=SelectView(minimum=minimum, interaction=interaction))


def generatetop10(category, mini):
    placement = 1
    if category == "Kills":
        t = sqlite.top_10_kills(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1
    if category == "Deaths":
        t = sqlite.top_10_deaths(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1
    if category == "KDR":
        t = sqlite.top_10_kdr(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1
    if category == "Wins":
        t = sqlite.top_10_wins(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1
    if category == "Losses":
        t = sqlite.top_10_losses(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1
    if category == "Games Played":
        t = sqlite.top_10_gp(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1
    if category == "WLR":
        t = sqlite.top_10_wlr(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1
    if category == "Rounds Played":
        t = sqlite.top_10_rp(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1
    if category == "KPR":
        t = sqlite.top_10_kpr(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1
    if category == "Average Elo":
        t = sqlite.top_10_avgelo(conn, mini)
        while placement <= len(t):
            yield f"{placement}. {t[placement - 1][0]} - {t[placement - 1][1]}\n"
            placement += 1


# This command subtracts 20 rating from a player
# Params: Takes a username as a string
# Params: User must be "Ranked Staff" to run this command
@bot.tree.command(name="minus20", description="Subtract 20 elo from a player")
@app_commands.describe(name="Username")
@app_commands.checks.has_any_role(525025520975609866, 827513306788266024, 1059228479163469945)
async def minus20(interaction: discord.Interaction, name: str):
    if audit is True:
        print("hi")
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /minus20 {name}")
    status = sqlite.minus20(conn, name)
    if status == "error":
        await interaction.response.send_message(f"Unable to update {name}'s elo")
        return
    if status == "success":
        await interaction.response.send_message(f"20 elo has been removed from {name}")
        update_rankings()
        return
    await interaction.response.send_message("Unknown Error has occurred")


# This command adds 20 rating to a player
# Params: Takes a username as a string
# Params: User must be "Ranked Staff" to run this command
# Note: add20 was written months before minus20 and it really shows in the code
@bot.tree.command(name="add20", description="Add 20 elo from a player")
@app_commands.describe(name="Username")
@app_commands.checks.has_any_role(525025520975609866, 827513306788266024, 1059228479163469945)
async def add20(interaction: discord.Interaction, name: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /add20 {name}")
    status = sqlite.add20(conn, name)
    if status == "error":
        await interaction.response.send_message(f"Unable to update {name}'s elo")
        return
    if status == "success":
        await interaction.response.send_message(f"20 elo has been added to {name}")
        update_rankings()
        return
    await interaction.response.send_message("Unknown Error has occurred")


#Displays how often the maps from the Ranked CvC map pool have been played
@bot.tree.command(name="maps", description="Check how often certain maps are played")
async def maps(interaction: discord.Interaction):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /maps")
    maps = sqlite.get_all_maps(conn)
    await interaction.response.send_message(
        f"Alleyway: {maps[0][0]}\nAtomic: {maps[1][0]}\nMirage: {maps[2][0]}\nCarrier: {maps[3][0]}\n"
        f"Cobblestone: {maps[4][0]}\n"
        f"Train: {maps[5][0]}\nOverpass: {maps[6][0]}\n"
        f"Overgrown: {maps[7][0]}\nCache: {maps[8][0]}\nAncient: {maps[9][0]}\n"
        f"Sandstorm: {maps[10][0]}\nTemple: {maps[11][0]}")


#Takes the username of every player and puts it on a text file in the directory where the bot is being run
#Params: User must have the "Admin" role to run this command
@bot.tree.command(name="exportusers", description="Generate a list of all registered players to a text file")
#@app_commands.checks.has_any_role(525025520975609866, 1059228479163469945)
async def exportusers(interaction: discord.Interaction):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /exportusers")
    #We create a file called "rankedCvCPlayers.txt" and write the name of every user separated by a newline in the file
    file = open("rankedCvCPlayers.txt", "w")
    info = sqlite.get_export(conn)
    for name, did in info:
        file.write(f"{name} {did}\n")
    #Once we're done, close the file and send a success message
    file.close()
    await interaction.response.send_message("Users successfully exported")


#Reads a text file that contains a username and then a newline, upon reading the username it registers a player
#Params: Takes a textfile as a string, the text file should be generated by the exportusers command
#Params: User must have the "Admin" role to run this command
@bot.tree.command(name="importusers", description="Import a list of users that will be automatically registered")
@app_commands.describe(textfile="Name of file to import")
@app_commands.checks.has_any_role(525025520975609866, 1059228479163469945)
async def importusers(interaction: discord.Interaction, textfile: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /importusers {textfile}")
    await interaction.response.defer()
    file = open(textfile, "r")
    lines = file.readlines()
    for y in lines:
        name, did = y.split(" ")
        print(name, did)
        sqlite.register(conn, name, did)
    file.close()
    update_rankings()
    await interaction.followup.send("Users successfully imported")


#This command takes in 10 usernames and sorts them by rating. The top 2 players are the captains
@bot.tree.command(name="captains", description="Check who the captains are (requires 10 names)")
async def captains(interaction: discord.Interaction):
    captains = []
    channelID = interaction.user.voice.channel.id
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /captains")
    if channelID == 827511070411194398 or channelID == 1059251513626738839 or channelID == 1203239964301860884:
        members = interaction.user.voice.channel.members
        memberID = []
        for i in members:
            memberID.append(i.id)
        captains = sqlite.captains(conn, memberID)
        gencap = generate_captains(captains)
        await interaction.response.send_message(("Top four captain candidates are: " + ", ".join(map(str, gencap))))
    else:
        await interaction.response.send_message("You are using this command from an invalid channel")
        return


def generate_captains(captains):
    i = 0
    for x in range(0, len(captains)):
        if i > 3:
            break
        if x != (len(captains)-1):
            yield f"{captains[x][0]}"
        i += 1


@bot.tree.command(name="auditon", description="Turn on the audit log")
@app_commands.checks.has_any_role(525025520975609866, 1059228479163469945)
async def auditon(interaction: discord.Interaction):
    global audit
    audit = True
    await interaction.response.send_message("Audit has been toggled on")
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /auditon")


@bot.tree.command(name="auditoff", description="Turn off the audit log")
@app_commands.checks.has_any_role(525025520975609866, 1059228479163469945)
async def auditoff(interaction: discord.Interaction):
    global audit
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /auditoff")
    audit = False
    await interaction.response.send_message("Audit has been toggled off")


@bot.tree.command(name="findname", description="Find the IGN of a registered user with their discord ID")
async def findname(interaction: discord.Interaction, did: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /findname {did}")
    name = sqlite.findname(conn, did)
    if name == "error":
        await interaction.response.send_message(f"There is no registered player with Discord ID: {did}")
        return
    await interaction.response.send_message(f"The IGN for {did} is {name}")


@bot.tree.command(name="findid", description="Find the Discord ID of a registered user with their MC IGN")
async def findid(interaction: discord.Interaction, ign: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /findid {ign}")
    did = sqlite.findid(conn, ign)
    if did == "error":
        await interaction.response.send_message(f"There is no registered player with IGN: {ign}")
        return
    await interaction.response.send_message(f"The DID for {ign} is {did}")


@bot.tree.command(name="makeparty", description="This command will give you 2 party commands to run to help you make a party for the ranked game")
async def makeparty(interaction: discord.Interaction):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /makeparty")
    party = []
    channelID = interaction.user.voice.channel.id
    if channelID == 827511070411194398 or 1059251513626738839 or 968279181274251274:
        members = interaction.user.voice.channel.members
        memberID = []
        for i in members:
            memberID.append(i.id)
        for j in memberID:
            name = sqlite.findname(conn, j)
            if name != "error":
                party.append(name)
        if len(party) < 10:
            await interaction.response.send_message("Not everyone in the channel is registered. Make sure to correct people have the correct ID's.")
            return
        if len(party) > 10:
            await interaction.response.send_message("Too many people in the channel.")
            return
        await interaction.response.send_message(f"`/party {party[0]} {party[1]} {party[2]} {party[3]} {party[4]}\n"
                                                f"/party {party[5]} {party[6]} {party[7]} {party[8]} {party[9]}`")
    else:
        await interaction.response.send_message("Not in valid channel to use this command")


@bot.tree.command(name="avgelo", description="Check a player's average elo per game")
async def avgelo(interaction: discord.Interaction, username: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /avgelo {username}")
    avgelo = sqlite.get_avgelo(conn, username.lower())
    if avgelo == "error":
        await interaction.response.send_message(f"There is no user with the name '{username}'")
        return
    await interaction.response.send_message(f"{username} averages {avgelo} elo/game")


@bot.tree.command(name="changeid", description="Change a players discord ID")
@app_commands.checks.has_any_role(525025520975609866, 827513306788266024, 1059228479163469945)
async def changeid(interaction: discord.Interaction, username: str, did: str):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /changeid {username} {did}")
    name = sqlite.check_valid_id(conn, did)
    if name != "error":
        await interaction.response.send_message(f"ID is already in use under user `{name[0][0]}`")
        return
    if sqlite.check_valid(conn, username) == "error":
        await interaction.response.send_message(f"Could not find user `{username}`")
        return
    status = sqlite.change_did(conn, username, did)
    if status == "error":
        await interaction.response.send_message(f"Unable to change the ID of `{username}`")
        return
    await interaction.response.send_message(f"{username} now has the Discord ID: {did}")


@bot.tree.command(name="purgeinactive", description="Remove all players with 0 games played")
@app_commands.checks.has_any_role(525025520975609866, 1059228479163469945)
async def purgeinactive(interaction: discord.Interaction):
    if audit is True:
        channel = bot.get_channel(1025102425352318986)
        await channel.send(f"{interaction.user.name} used /purgeinactive")
    status = sqlite.purge_inactive(conn)
    if status == "success":
        await interaction.response.send_message("The Purge has been completed")
        return
    await interaction.response.send_message("Unknown Error")


bot.run(TOKEN)
