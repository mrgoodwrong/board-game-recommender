# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 10:28:04 2017

@author: Tadej Pesjak
"""
import BGRecommenderData
import pandas as pd
import re
from sklearn.metrics.pairwise import euclidean_distances

def col2list(column, df):
    split = df[column].apply(lambda x: x.split(", "))
    cat_list = []
    for i in list(split):
        for j in i:
            if j not in cat_list:
                cat_list.append(j)
    return cat_list

def clean_list(original_list):
    end_list = []
    for i in original_list:
        name = i.lower()
        name = re.sub('[^A-Za-z0-9\s]+', '', name)
        end_list.append(name)
    return end_list

def only_my_games(clean, df):
    idxs = []
    for index, game in df.iterrows():
        game = game["clean_name"].split(" ")
        for i in clean:
            split = i.split(" ")
            if len(game) == len(split):
                if all(x in game for x in split):
                    idxs.append(index)
    my_games_df = df.iloc[idxs]
    return my_games_df
    

def average_game(list_of_games, df):
    
    """
    This function takes the data from the inputted games and creates a one row Average Game.
    The numerical data is averaged and the categorical data added together into a list.
    """
    
    pd.options.mode.chained_assignment = None # default='warn'
    clean = clean_list(list_of_games)
    all_games = only_my_games(clean, df)
    average_game = all_games.iloc[0]
    mechanics = col2list("mechanic", all_games)
    category = col2list("category", all_games)
    designer = col2list("designer", all_games)
    average_game["names"] = "My Games"
    average_game["mechanic"] = mechanics
    average_game["category"] = category
    average_game["designer"] = designer
    average_game["mechanics_list"] = mechanics
    average_game["categories_list"] = category
    average_game["designers_list"] = designer
    average_game["avg_rating"] = all_games["avg_rating"].max()
    average_game["geek_rating"] = all_games["geek_rating"].max()
    average_game["clean_name"] = "my games"
    average_game[["min_players", "max_players", "year", "age", "weight", "play_time", "know_game"]] = all_games[["min_players", "max_players", "year", "age", "weight", "play_time", "know_game"]].mean()
    return average_game

def corresponding_games(games_list, data):
    
    """
    This function iterrates through the categorical data in the inputted games dataframe
    and filters it so that only games which contain the mechanics, categories or the designers
    from the Average Game are left. Because not all designers have been used,
    the designer category has to pass a check.
    
    A dataframe with only these games is returned.
    """
    
    my_game = average_game(games_list, data)
    #only rows with my mechanics, categories and designers
    mechanics = my_game["mechanic"]
    categories = my_game["category"]
    designers = my_game["designer"]
    final_games = []
    for i in mechanics:
        for j in categories:
            for k in designers:
                try:
                    if k in list(data.columns):
                        result = data[((data[i] == 1) | (data[j] == 1)) | (data[k] == 1)]
                        if len(result) > 0:
                            games = list(result.index)
                            for i in games:
                                if i not in final_games:
                                    final_games.append(i)
                    else:
                        result = data[(data[i] == 1) | (data[j] == 1)]
                        if len(result) > 0:
                            games = list(result.index)
                            for i in games:
                                if i not in final_games:
                                    final_games.append(i)
                except Exception:
                    pass
    cor_games = data.loc[final_games]
    return (cor_games, my_game)
    
def recommend_games(games_list, data):
    
    """
    This function uses Euclidean distance to calculate the similarity between the Average Game
    and the games left after the categorial data filtering. 
    """
    
    df_and_example = corresponding_games(games_list, data)
    cor_games = df_and_example[0]
    my_game = df_and_example[1]
    clean = clean_list(games_list)
    features = ['min_players', 'max_players', 'year', 'avg_rating', 'geek_rating', 'age', 'weight', 'play_time', 'know_game']
    my_example = my_game[features]
    games = cor_games[features]
    distances = []
    for i in range(0, len(games)):
        second_game = games.iloc[i]
        second_game = second_game.values.reshape((1, -1))
        my_example = my_example.reshape((1, -1))
        distance = euclidean_distances(my_example, second_game)
        distances.append(distance[0][0])
    cor_games["distances"] = distances
    cor_games = cor_games.sort_values("distances")
    
    # To avoid recommending an already inputted game, these are removed from the results.
    idxs = []
    for i in clean:
        index = cor_games[cor_games["clean_name"] == i].index
        idxs.append(index)
        cor_games.drop(index, inplace=True)
    return cor_games

if __name__ == '__main__':
    data = BGRecommenderData.GetDataSet()
    print("Add your favorite games. After you are finished, type 'end'.")
    FavoriteGames = []
    s = None
    while s != "end":
        s = input("Add game: ")
        if s not in list(data.clean_name) and s != "end":
            print("Sorry, game not found. Please try again!")
        FavoriteGames.append(s)
    print("Calculating your recommendations. Please wait.")
    RecommendedGames = recommend_games(FavoriteGames, data)
    RecommendedList = list(RecommendedGames.head(20)["names"])
    print(" ")
    print(" ")
    print(" ")
    print("We recommend you check out the following games:")
    count = 1
    for i in RecommendedList:
        print(str(count) + ". " + i)
        count += 1
    
    
