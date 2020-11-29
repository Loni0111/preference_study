#!/usr/bin/env python
# coding: utf-8

# Cleaning data into pandas dataframe format
import os
import pandas as pd
from PIL import Image
import numpy as np

# read test data from the csv files in the result data folder
# put the data into dataframe and filter out desired variables 

# There are three categories
categories = ['flowers', 'houses', 'paints']

# Input: .csv files containing the raw data directly downloaded from pavlovia.org
# Output: Dataframe file with selected items for all participants 
def Data2Df(categoryList):
    dfRaw = pd.DataFrame()
    for category in categoryList:
        directory = category + "/data/"

        for root,dirs,files in os.walk(directory):
            for file in files:
                if file.endswith(".csv"):
                    dfParticipant = pd.read_csv(directory + file)
                
                    # add category column
                    dfParticipant['category'] = category             
                    dfRaw = dfRaw.append(dfParticipant)
                    
    # filter out useful information from raw data
    df = dfRaw[['key_resp_2.keys', 
                'key_resp_2.rt', 
                'image_left', 
                'image_right', 
                'trial_num', 
                'participant', 
                'date',
                'category']]
    
    # change column name to better organize data
    df = df.rename(columns={'key_resp_2.keys': 'score', 'key_resp_2.rt': 'time'})
    
    # Disable warning due to potential 'chained' assignments in Dataframe
    pd.options.mode.chained_assignment = None 
    df['score'] = df['score'].replace(['z', 'm'],[1, 0])
    
    return df


# Input: Dataframe from the output of Data2Df function
# Output: Dataframe containing the score of each image
def Df2Score(df):
    # create score table for left image and right image, respectively
    # the current score is calculated with basic average score of each
    # image, more advanced math model can be applied to better differentiate 
    # the performance of each image.
    key = df['key_resp_2.keys']

    leftScore = key.replace(['z','m'], [1,0])
    rightScore = key.replace(['z','m'], [0,1])

    # create image to score dataframe
    imageDir = list(df['image_left']) + list(df['image_right'])
    score = list(leftScore) + list(rightScore)
    dfScore = pd.DataFrame({'imageDir':imageDir, 'score':score})
    dfScore = dfScore.groupby('imageDir').mean()
    
    return dfScore


# image resize for computation efficiency 
# The function create a folder for resized images.
# Only execute one time
def imageResize(categoryList):
    
    for category in categories:
        path = category + '/images/'
    
        # create a new folder for resized images
        newpath = category + '/images_resized/'
        os.makedirs(newpath)
        dirs = os.listdir(path)

        for item in dirs:
            if os.path.isfile(path+item):
                im = Image.open(path+item)
                f, e = os.path.splitext(item)
                imResize = im.resize((100,100), Image.ANTIALIAS)
                imResize.save(newpath + '/' + f + '.jpg', 'JPEG', quality=90)
                
                
# Input: image file
# Output: 3 dimensional array (tricolour, pixel_rawIndex, pixel_colIndex)
def jpg_2_arr(file):
    img=Image.open(file)
    r,g,b=img.split()

    r_arr=np.array(r).reshape(100*100)
    g_arr=np.array(g).reshape(100*100)
    b_arr=np.array(b).reshape(100*100)

    img_arr=np.concatenate((r_arr,g_arr,b_arr))
    result=img_arr.reshape((3,100,100))
    return result

