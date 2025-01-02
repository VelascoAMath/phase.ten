import argparse
import collections
import os
import pickle as pkl
from configparser import ConfigParser

import pandas as pd
import peewee

from GameMessage import GameMessage
from Gamephasedecks import Gamephasedecks
from Games import Games
from Players import Players
from Users import Users

"""
This program will save or load the database.
This is in order to ensure that we can work with the same data across different devices.
This program will save the postgresql database rows in pandas tables and pickle them into a file.
The process is reversed so that the rows can be inserted into a postgresql database
"""


def save_db(database_file: str):
    """
    Save the postgresql database into a specified file
    :param database_file: where the database should be saved
    """
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", 1000)

    data = collections.defaultdict(list)
    for row in Users.select():
        for key, val in row.to_json_dict().items():
            data[key].append(val)

    users_df = pd.DataFrame(data)

    data = collections.defaultdict(list)
    for row in Games.select():
        for key, val in row.to_json_dict().items():
            data[key].append(val)

    games_df = pd.DataFrame(data)

    data = collections.defaultdict(list)
    for row in Players.select():
        for key, val in row.to_json_dict().items():
            data[key].append(val)

    players_df = pd.DataFrame(data)

    data = collections.defaultdict(list)
    for row in GameMessage.select():
        for key, val in row.to_json_dict().items():
            data[key].append(val)

    gm_df = pd.DataFrame(data)

    data = collections.defaultdict(list)
    for row in Gamephasedecks.select():
        for key, val in row.to_json_dict().items():
            data[key].append(val)

    gpd_df = pd.DataFrame(data)

    with open(database_file, "wb") as f:
        pkl.dump([users_df, games_df, players_df, gpd_df, gm_df], f)


def load_db(database_file: str):
    """
    Given a pickled file, insert the rows into the postgresql server
    :param database_file: the pickled file containing the rows
    """
    parser = ConfigParser()
    config = {}

    parser.read("database.ini")
    if parser.has_section("postgresql"):
        for param in parser.items("postgresql"):
            config[param[0]] = param[1]
    else:
        raise Exception(f"No postgresql section in database.ini!")

    db = peewee.PostgresqlDatabase(**config)
    db.create_tables([Users, Games, Players, Gamephasedecks, GameMessage])

    with open(database_file, "rb") as f:
        df_list: list[pd.DataFrame] = pkl.load(f)
        users_df = df_list[0]
        games_df = df_list[1]
        players_df = df_list[2]
        gpd_df = df_list[3]
        gm_df = df_list[4]

    for _, row in users_df.iterrows():
        # Just in case we have an old version of the table
        if "display" not in row:
            row["display"] = row["name"]
        user = Users.from_json_dict(row)
        if not Users.exists(user.id):
            user.save_as_is(force_insert=True)

    for _, row in games_df.iterrows():
        game = Games.from_json_dict(row)
        if not Games.exists(game.id):
            game.save_as_is(force_insert=True)

    for _, row in players_df.iterrows():
        game = Players.from_json_dict(row)
        if not Players.exists(game.id):
            game.save_as_is(force_insert=True)

    for _, row in gpd_df.iterrows():
        game = Gamephasedecks.from_json_dict(row)
        if not Gamephasedecks.exists(game.id):
            game.save_as_is(force_insert=True)

    for _, row in gm_df.iterrows():
        game = GameMessage.from_json_dict(row)
        if not GameMessage.exists(game.id):
            game.save_as_is(force_insert=True)


def main():
    parser = argparse.ArgumentParser(
        prog="TransferDB",
        description="A helpful little program to save to the disk and load to the phase ten database",
    )

    parser.add_argument(
        "action",
        choices=["save", "load"],
        help="The action to take. We can either save the database "
        "or load to it from a file",
    )
    parser.add_argument(
        "filename",
        nargs="?",
        default="database.pkl",
        help="The file where the database will be saved/loaded. By default, it is set to database.pkl",
    )

    parsed_args = parser.parse_args()

    filename, file_extension = os.path.splitext(parsed_args.filename)
    if file_extension != ".pkl":
        database_file = f"{filename}.pkl"
    else:
        database_file = parsed_args.filename

    if parsed_args.action == "save":
        save_db(database_file)
    else:
        load_db(database_file)


if __name__ == "__main__":
    main()
