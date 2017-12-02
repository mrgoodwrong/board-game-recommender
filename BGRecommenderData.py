# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 09:55:00 2017

@author: Tadej
"""

import pandas as pd
import re

def counts(col, list_of):
    dictionary = {}
    for i in list_of:
        for j in col:
            if i in j:
                if i not in dictionary:
                    dictionary[i] = 1
                else:
                    dictionary[i] += 1
    return dictionary

def GetDataSet():
    
    """
    Reading in and cleaning the dataset. 
    1. Adding new features
    2. For categorical data changing strings to lists
        - The exception is the designer category. Due to the large size of the category,
        less known designers have been grouped together.
    3. Transforming categorical data from lists to dummy variables to ensure faster procesing.

    """
    
    data = pd.read_csv("bgg_db_2017_04.csv" ,encoding = "latin-1")
    
    # New features
    data["play_time"] = (data["avg_time"] + data["min_time"] + data["max_time"]) / 3
    data["know_game"] = (data["num_votes"] + data["owned"]) / 2
    data = data.drop (["bgg_url", "game_id","image_url","rank", "avg_time","min_time","max_time", "num_votes","owned"], axis = 1)
    data["clean_name"] = data["names"].apply(lambda x: x.lower())
    data["clean_name"] = data["clean_name"].apply(lambda x: re.sub('[^A-Za-z0-9\s]+', '', x))
    num_features = ["min_players", "max_players","year", "avg_rating", "geek_rating", "age", "weight",  "play_time", "know_game"]
    data[num_features] = data[num_features] / data[num_features].max()
    
    # Transformig categorical data from strings to lists
    mechanic = data.mechanic.apply(lambda x: x.split(", "))
    mechanics_list = []
    for i in list(mechanic):
        for j in i:
            if j not in mechanics_list:
                mechanics_list.append(j)            
    data["mechanics_list"] = mechanic
    category = data.category.apply(lambda x: x.split(", "))
    categories_list = []
    for i in list(category):
        for j in i:
            if j not in categories_list:
                categories_list.append(j)           
    data["categories_list"] = category
    designer = data.designer.apply(lambda x: x.split(", "))
    designers_list = []
    for i in list(designer):
        for j in i:
            if j not in designers_list:
                designers_list.append(j)
                
    # Grouping less known designers together
    designers_list.remove("Jr.")           
    data["designers_list"] = designer
    designers_counts = counts(data["designers_list"], designers_list) 
    designers_counts_concise = {}
    designers_counts_concise["less_known"] = 0
    for i in designers_counts:
        if designers_counts[i] < 20:
            designers_counts_concise["less_known"] += designers_counts[i]
        else:
            designers_counts_concise[i] = designers_counts[i]
    del designers_counts_concise["less_known"]
    del designers_counts_concise["none"]
    del designers_counts_concise["(Uncredited)"]
    designers_list_concise = designers_counts_concise
    
    # Transforming to dummy variables
    for i in mechanics_list:
        data[i] = None
    for j in categories_list:
        data[j] = None
    for k in designers_list_concise:
        data[k] = None  
    for i in designers_list_concise:
        data[i] = data["designers_list"].apply(lambda x: 1 if i in x else 0)
    for i in categories_list:
        data[i] = data["categories_list"].apply(lambda x: 1 if i in x else 0)    
    for i in mechanics_list:
        data[i] = data["mechanics_list"].apply(lambda x: 1 if i in x else 0)
    return data

if __name__ == '__main__':
    data = GetDataSet()
    print(data.head())

  