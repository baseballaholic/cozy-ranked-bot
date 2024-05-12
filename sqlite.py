import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_players(conn, players):
    sql = f''' INSERT INTO players(did,username,kills,deaths,kdr,wins,losses,rank,rating,gp,wlr,rp,kpr,avgelo)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, players)
    conn.commit()
    return cur.lastrowid


def create_map(conn, map):
    sql = f''' INSERT INTO maps(name,times_played) 
             VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, map)
    conn.commit()
    return cur.lastrowid


def create_top_20(conn, score):
    sql = f''' INSERT INTO top20(id,name,kills,deaths,pm,date)
             VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, score)
    conn.commit()
    return cur.lastrowid


def create_top_20_pm(conn, score):
    sql = f''' INSERT INTO top20pm(id,username,kills,deaths,pm,date)
             VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, score)
    conn.commit()
    return cur.lastrowid


def update_players(conn, player):
    sql = ''' UPDATE players
              SET did = ?
              WHERE did = ?'''
    cur = conn.cursor()
    cur.execute(sql, player)
    conn.commit()


def update_rankings(conn, player, rank):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET rank = ?
              WHERE username = ?'''
    p = (rank, player)
    cur.execute(sql, p)
    conn.commit()
    return "success"

def update_top20_ids(conn, oldID, newID):
    cur = conn.cursor()
    sql = ''' UPDATE top20
              SET id = ?
              WHERE id = ?'''
    ids = (newID, oldID)
    cur.execute(sql, ids)
    conn.commit()
    return "success"


def update_top20pm_ids(conn, oldID, newID):
    cur = conn.cursor()
    sql = ''' UPDATE top20pm
              SET id = ?
              WHERE id = ?'''
    ids = (newID, oldID)
    cur.execute(sql, ids)
    conn.commit()
    return "success"


def update_kills(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET kills = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_deaths(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET deaths = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_kdr(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET kdr = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_wins(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET wins = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_losses(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET losses = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_rank(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET rank = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_rating(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET rating = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_gp(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET gp = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_wlr(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET wlr = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_rp(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET rp = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_kpr(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET kpr = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def update_avgelo(conn, player):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET avgelo = ?
              WHERE LOWER(username) = ?'''
    cur.execute(sql, player)
    conn.commit()
    return "success"


def change_name(conn, oldname, newname):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET username = ?
              WHERE LOWER(username) = ?'''
    p = (newname, oldname.lower())
    try:
        cur.execute(sql, p)
        conn.commit()
    except:
        return "unknown error"
    return "success"


def change_did(conn, username, did):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET did = ?
              WHERE LOWER(username) = ?'''
    p = (did, username.lower())
    try:
        cur.execute(sql, p)
        conn.commit()
    except:
        return "error"
    return "success"


def set(conn, stats):
    cur = conn.cursor()
    sql = ''' UPDATE players
              SET kills = ?,
              deaths = ?,
              kdr = ?,
              wins = ?,
              losses = ?,
              rank = ?,
              rating = ?,
              gp = ?,
              wlr = ?,
              rp = ?,
              kpr = ?,
              avgelo = ?
              WHERE LOWER(username) = ?
              '''
    try:
        cur.execute(sql, stats)
        conn.commit()
    except:
        return "error"
    return "success"


def minus20(conn, name):
    cur = conn.cursor()
    rating = get_rating(conn, name)
    if rating == "error":
        return "error"
    sql = ''' UPDATE players
              SET rating = ?
              WHERE LOWER(username) = ?'''
    p = (rating-20, name.lower())
    try:
        cur.execute(sql, p)
        conn.commit()
    except:
        return "error"
    return "success"


def add20(conn, name):
    cur = conn.cursor()
    rating = get_rating(conn, name)
    if rating == "error":
        return "error"
    sql = ''' UPDATE players
              SET rating = ?
              WHERE LOWER(username) = ?'''
    p = (rating+20, name.lower())
    try:
        cur.execute(sql, p)
        conn.commit()
    except:
        return "error"
    return "success"



def get_did(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT did FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    did = cur.fetchone()
    return did


def get_username(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT username FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    username = cur.fetchone()
    return username


def get_kills(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT kills FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    kills = cur.fetchone()
    return kills[0]


def get_deaths(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT deaths FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    deaths = cur.fetchone()
    return deaths[0]


def get_kdr(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT kdr FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    kdr = cur.fetchone()
    return kdr[0]


def get_wins(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT wins FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    wins = cur.fetchone()
    return wins[0]


def get_losses(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT losses FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    losses = cur.fetchone()
    return losses[0]


def get_rank(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT rank FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    rank = cur.fetchone()
    return rank[0]


def get_rating(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT rating FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    rating = cur.fetchone()
    if rating == "[]" or rating == None:
        return "error"
    return rating[0]


def get_gp(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT gp FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    gp = cur.fetchone()
    return gp[0]


def get_wlr(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT wlr FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    wlr = cur.fetchone()
    return wlr[0]


def get_rp(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT rp FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    rp = cur.fetchone()
    return rp[0]


def get_kpr(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT kpr FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    kpr = cur.fetchone()
    return kpr[0]


def get_avgelo(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT avgelo FROM players WHERE LOWER(username) = ?", (name.lower(), ))
    avgelo = cur.fetchone()
    if avgelo == "[]" or avgelo == None:
        return "error"
    return avgelo[0]


def get_add_stats(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT kills,deaths,rating,wins,losses,gp,rp FROM players WHERE LOWER(username)=?", (name.lower(),))
    query = cur.fetchone()
    return query


def get_times_played(conn, map):
    cur = conn.cursor()
    cur.execute("SELECT times_played FROM maps WHERE LOWER(name) = ?", (map.lower(),))
    times_played = cur.fetchone()
    return times_played[0]


def get(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE LOWER(username) = ?", (name.lower(),))
    player = cur.fetchone()
    if player == "[]" or player == None:
        return "error"
    return player


def get_all_maps(conn):
    cur = conn.cursor()
    cur.execute("SELECT times_played FROM maps")
    maps = cur.fetchall()
    return maps


def get_export(conn):
    cur = conn.cursor()
    cur.execute("SELECT username, did FROM players")
    info = cur.fetchall()
    return info


def generate_top_20_kills(conn, end):
    cur = conn.cursor()
    cur.execute("SELECT * FROM top20 ORDER BY kills DESC, deaths ASC, date ASC")
    top20kills = cur.fetchmany(end)
    return top20kills


def generate_top_20_pm(conn, end):
    cur = conn.cursor()
    cur.execute("SELECT * FROM top20pm ORDER BY pm DESC, kills DESC, date ASC")
    top20pm = cur.fetchmany(end)
    return top20pm


def top_10_kills(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, kills FROM players WHERE gp >= ? ORDER BY kills DESC", (mini,))
    query = cur.fetchmany(10)
    return query

def top_10_deaths(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, deaths FROM players WHERE gp >= ? ORDER BY deaths DESC", (mini,))
    query = cur.fetchmany(10)
    return query

def top_10_kdr(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, kdr FROM players WHERE gp >= ? ORDER BY kdr DESC", (mini,))
    query = cur.fetchmany(10)
    return query


def top_10_wins(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, wins FROM players WHERE gp >= ? ORDER BY wins DESC", (mini,))
    query = cur.fetchmany(10)
    return query


def top_10_losses(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, losses FROM players WHERE gp >= ? ORDER BY losses DESC", (mini,))
    query = cur.fetchmany(10)
    return query


def top_10_gp(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, gp FROM players WHERE gp >= ? ORDER BY gp DESC", (mini,))
    query = cur.fetchmany(10)
    return query


def top_10_wlr(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, wlr FROM players WHERE gp >= ? ORDER BY wlr DESC", (mini,))
    query = cur.fetchmany(10)
    return query


def top_10_rp(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, rp FROM players WHERE gp >= ? ORDER BY rp DESC", (mini,))
    query = cur.fetchmany(10)
    return query


def top_10_kpr(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, kpr FROM players WHERE gp >= ? ORDER BY kpr DESC", (mini,))
    query = cur.fetchmany(10)
    return query


def top_10_avgelo(conn, mini):
    cur = conn.cursor()
    cur.execute("SELECT username, avgelo FROM players WHERE gp >= ? ORDER BY avgelo DESC", (mini,))
    query = cur.fetchmany(10)
    return query


def delete_players(conn, name):
    """
    Delete a task by task id
    :param conn:  Connection to the SQLite database
    :param id: id of the task
    :return:
    """
    sql = 'DELETE FROM players WHERE LOWER(username)=?'
    cur = conn.cursor()
    cur.execute(sql, (name.lower(),))
    conn.commit()


def delete_all_players(conn):
    """
    Delete all rows in the tasks table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM players'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def purge_inactive(conn):
    cur = conn.cursor()
    cur.execute("SELECT username FROM players WHERE gp=0")
    rows = cur.fetchall()
    for row in rows:
        delete(conn, row)
    return "success"


def select_all_players(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM players")

    rows = cur.fetchall()

    for row in rows:
        print(row)


def select_all_players_by_rating(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM players ORDER BY rating DESC")
    query = cur.fetchall()
    return query

def select_all_top_20_by_id(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM top20 ORDER BY id ASC")
    query = cur.fetchall()
    return query

def select_all_top_20_pm_by_id(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM top20pm ORDER BY id ASC")
    query = cur.fetchall()
    return query

def select_all_maps(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM maps")

    rows = cur.fetchall()

    for row in rows:
        print(row)


def drop_table_players(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE players")
    conn.commit()


def total_players(conn):
    cur = conn.cursor()
    cur.execute("SELECT Count(*) FROM players")
    total = cur.fetchone()
    return total[0]


def total_top_20(conn):
    cur = conn.cursor()
    cur.execute("SELECT Count(*) FROM top20")
    total = cur.fetchone()
    return total[0]


def total_top_20_pm(conn):
    cur = conn.cursor()
    cur.execute("SELECT Count(*) FROM top20pm")
    total = cur.fetchone()
    return total[0]


def lowest_top_20_kills(conn):
    cur = conn.cursor()
    cur.execute("SELECT kills FROM top20 ORDER BY kills DESC")
    kills = cur.fetchall()
    i = 1
    for row in kills:
        if i == 20:
            return row[0]
        i = i + 1
    return 0

def lowest_top_20_pm(conn):
    cur = conn.cursor()
    cur.execute("SELECT pm FROM top20pm ORDER BY pm DESC")
    kills = cur.fetchall()
    i = 1
    for row in kills:
        if i == 20:
            return row[0]
        i = i + 1
    return 0

def r(conn, username: str = None, did: str = None):
    cur = conn.cursor()
    if did != None:
        username = findname(conn, did)
        if username == "error":
            return "error"
    cur.execute("SELECT username,rank,rating,kdr,wins,losses,wlr,kpr FROM players WHERE did=? OR LOWER(username)=?",
                (did, username.lower(),))
    query = cur.fetchone()
    if query == None:
        return "error"
    return query


def register(conn, username, did):
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE LOWER(username)=? OR did=?", (username.lower(), did))
    query = cur.fetchall()
    if str(query) != "[]":
        return "error"
    rank = total_players(conn)
    player = (did, username, 0, 0, 0, 0, 0, rank + 1, 1500, 0, 0, 0, 0, 0)
    player_id = create_players(conn, player)
    return "success"


def delete(conn, username):
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE LOWER(username)=?", (username.lower(),))
    query = cur.fetchall()
    if str(query) == "[]":
        return "error"
    delete_players(conn, username)
    return "success"


def delete_top_20(conn, tid):
    sql = 'DELETE FROM top20 WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (tid,))
    conn.commit()
    return "success"


def delete_top_20_pm(conn, tid):
    sql = 'DELETE FROM top20pm WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (tid,))
    conn.commit()
    return "success"


def forceregister(conn, username, id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE LOWER(username)=? OR did=?", (username.lower(), id))
    query = cur.fetchall()
    if str(query) != "[]":
        return "error"
    rank = total_players(conn)
    player = (id, username, 0, 0, 0, 0, 0, rank + 1, 1500, 0, 0, 0, 0, 0)
    player_id = create_players(conn, player)
    return "success"


def lb(conn, username):
    cur = conn.cursor()
    cur.execute("SELECT rank FROM players WHERE LOWER(username)=?", (username.lower(),))
    query = cur.fetchone()
    if str(query) == "[]" or query == None:
        return "error"
    return query


def generatecustomlb(conn, rank):
    cur = conn.cursor()
    start = rank - 20
    end = rank + 19
    total = total_players(conn)
    if rank - 20 < 1:
        start = 1
    if rank + 19 > total:
        end = total
    cur.execute("SELECT rank, rating, username FROM players WHERE rank BETWEEN ? and ? ORDER BY rank ASC", (start, end))
    query = cur.fetchall()
    if str(query) == "[]":
        return "error"
    return query


def generatelb(conn, start, end):
    cur = conn.cursor()
    cur.execute("SELECT rank, username, rating FROM players WHERE rank BETWEEN ? and ? ORDER BY rank ASC", (start, end))
    query = cur.fetchall()
    if str(query) == "[]":
        return "error"
    return query


def updatemap(conn, map, times_played):
    sql = ''' UPDATE maps
                  SET times_played = ?
                  WHERE LOWER(name) = ?'''
    cur = conn.cursor()
    insert = (times_played, map.lower())
    cur.execute(sql, insert)
    conn.commit()
    return "success"


def reset_season_players(conn):
    cur = conn.cursor()
    cur.execute("SELECT did FROM players")
    players = cur.fetchall()
    sql = ''' UPDATE players
                SET kills = 0,
                deaths = 0,
                kdr = 0,
                wins = 0,
                losses = 0,
                rating = 1500,
                gp = 0,
                wlr = 0,
                rp = 0,
                kpr = 0
                WHERE did = ?'''
    for did in players:
        cur.execute(sql, did)
        conn.commit()
    return "Players Reset"


def reset_season_maps(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM maps")
    maps = cur.fetchall()
    sql = ''' UPDATE maps
                SET times_played = 0
                WHERE name=?'''
    for name in maps:
        cur.execute(sql, name)
        conn.commit()
    return "Maps Reset"


def reset_season_top_20(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM top20")
    top20 = cur.fetchall()
    sql = ''' DELETE FROM top20 WHERE id=?'''
    for score in top20:
        cur.execute(sql, score)
        conn.commit()
    return "Top 20 Reset"


def reset_season_top_20_pm(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM top20pm")
    top20 = cur.fetchall()
    sql = ''' DELETE FROM top20pm WHERE id=?'''
    for score in top20:
        cur.execute(sql, score)
        conn.commit()
    return "Top 20 PM Reset"


def check_valid(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE LOWER(username) = ?", (name.lower(),))
    query = cur.fetchall()
    if str(query) == "[]" or query == None:
        return "error"
    return "success"


def check_valid_id(conn, did):
    cur = conn.cursor()
    cur.execute("SELECT username FROM players WHERE did=?", (did,))
    query = cur.fetchall()
    if str(query) == "[]" or query == None:
        return "error"
    return query


def check_valid_top_20(conn, kills, user, deaths):
    cur = conn.cursor()
    cur.execute("SELECT id FROM top20 WHERE kills = ? and LOWER(name) = ? and deaths = ? ORDER BY id DESC", (kills, user.lower(), deaths))
    query = cur.fetchone()
    if str(query) == "[]" or query == None:
        return "error", 0
    return "success", query[0]


def check_valid_top_20_pm(conn, kills, user, deaths):
    cur = conn.cursor()
    cur.execute("SELECT id FROM top20pm WHERE kills = ? and LOWER(username) = ? and deaths = ? ORDER BY id DESC", (kills, user.lower(), deaths))
    query = cur.fetchone()
    if str(query) == "[]" or query == None:
        return "error", 0
    return "success", query[0]


def findname(conn, did):
    cur = conn.cursor()
    cur.execute("SELECT username FROM players WHERE did=?", (did,))
    query = cur.fetchone()
    if str(query) == "[]" or query == None:
        return "error"
    return query[0]


def findid(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT did FROM players WHERE LOWER(username)=?", (name.lower(),))
    query = cur.fetchone()
    if str(query) == "[]" or query == None:
        return "error"
    return query[0]


def captains(conn, dids):
    cur = conn.cursor()
    cur.execute("SELECT username FROM players WHERE gp > 6 and (did=? or did=? or did=? or did=? or did=? or did=? or did=? or did=? or did=? or did=?) ORDER BY rating DESC",
                (dids[0], dids[1], dids[2], dids[3], dids[4], dids[5], dids[6], dids[7], dids[8], dids[9]))
    caps = cur.fetchall()
    return caps


def main():
    database = "test.db"

    conn = create_connection(database)
    # with conn:
    # drop_table_players(conn)
    sql_create_top20pm_table = """ CREATE TABLE IF NOT EXISTS top20pm (
                                            id integer PRIMARY KEY,
                                            username text NOT NULL,
                                            kills integer NOT NULL,
                                            deaths integer NOT NULL,
                                            pm integer NOT NULL,
                                            date text NOT NULL
                                        ); """
    sql_create_maps_table = """ CREATE TABLE IF NOT EXISTS maps (
                                            name text PRIMARY KEY,
                                            times_played integer NOT NULL
                                        ); """
    if conn is not None:
        #create projects table
        create_table(conn, sql_create_top20pm_table)
    with conn:
        # amap = ("Alleyway", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Atomic", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Mirage", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Carrier", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Cobblestone", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Train", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Overpass", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Overgrown", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Cache", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Ancient", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Sandstorm", 0)
        # map_id = create_map(conn, amap)
        # amap = ("Temple", 0)
        # map_id = create_map(conn, amap)
        print("1. Query all maps")
        select_all_maps(conn)

    # with conn:
    #     update_players(conn, (2, 183640646836420608))
    with conn:
        # player = ('1', "baseballaholic", 0, 0, 0, 0, 0, 1, 1500, 0, 0, 0, 0, 0)
        # player_id = create_players(conn, player)
        # player = ('2', "hants", 0, 0, 0, 0, 0, 2, 1500, 0, 0, 0, 0, 0)
        # player_id = create_players(conn, player)
        # player = ('3', "MSBen", 0, 0, 0, 0, 0, 3, 1500, 0, 0, 0, 0, 0)
        # player_id = create_players(conn, player)
        print("2. Query all players")
        select_all_players(conn)
    # with conn:
    # delete_players(conn, 183640646836420608)
    # delete_all_players(conn)


if __name__ == '__main__':
    main()
