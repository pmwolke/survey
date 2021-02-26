# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 09:39:36 2021

@author: Wolke
"""
# Import needed libraries
import numpy as np
import pandas as pd
import re
import time
import matplotlib.pyplot as plt

# Dictionary for each set of answer choices
yes_no_dict = {"Yes": 1, "No":0}
likeart_5_dict = {"Very likely": 5, "Somewhat likely": 4, "Neither likely nor unlikely": 3,
                "Somewhat unlikely": 2, "Very unlikely": 1}
q6_dict = {"Pieces": 0, "Pounds": 1, "Other, please specify": 0}
q7_dict = {"2 leg quarters": 1, "3-4 leg quarters": 2, "5 pound bag": 3, "10 pound bag": 4,
           "More than one 10 pound bag": 5}
how_often_dict = {"Less than once a year": 0, "Once a year": 1, "Once every 6 months": 2,
                  "Once every 2-3 months": 3, "Once a month": 4, "2-3 times a month": 5,
                  "Once every week": 6, "Multiple times per week": 7}
q13_dict = {"Refrigerated (in the meat aisle with the other fresh meats)": 1, "No preference, I buy both equally": 2,
            "Frozen (in the frozen aisle with other uncooked frozen meats)": 3}
q14_dict = {"Bag": 1, "Tray": 2, "From the meat counter": 3, "No preference, I buy all equally": 4}
q16_dict = {"One at a time": 1, "2-3 at a time": 2, "More than 3 at a time": 3, "All of my leg quarters at a time": 4}
q20_dict = {"Just myself or someone else in my family": 1, "2 people": 2, "3 people": 3,
            "4 people": 4, "5 people": 5, "6 people": 6, "7 or more people": 7}
q22_dict = {"Much less likely": 1, "Somewhat less likely": 2, "About the same": 3, "Somewhat more likely": 4,
            "Much more likely": 5}
q23_dict = {"Much less": 1, "Somewhat less": 2, "About the same": 3, "Somewhat more": 4,
            "Much more": 5}

# Schema is for dictionary is  question_number:[question_text, answer_choices_dictionary]
question_dict = {1: ["At which of the following grocery stores have you shopped in the 6 months year?", yes_no_dict],
                 2: ["What departments have you purchased from in the last 6 months?", yes_no_dict],
                 3: ["How likely are you to purchase each of the following chicken items from the meat/frozen "\
                     "department in the next 6 months?", likeart_5_dict],
                 4: ["Which of the following chicken items have you purchased from the meat/frozen department "\
                     "in the last 6 months?", yes_no_dict],
                 6: ["When you are thinking about buying leg quarters, do you think about how many pieces you "\
                     "need to buy or how many pounds you need to buy?", q6_dict],
                 7: ["How many leg quarters do you typically buy at one time?", q7_dict],
                 8: ["When you buy leg quarters, are you buying them instead of other chicken or meat cuts?", yes_no_dict],
                 9: ["If you decide to buy something else instead of leg quarters, what do you typically buy?", yes_no_dict],
                 10: ["How often do you purchase leg quarters?", how_often_dict],
                 11: ["When do you buy leg quarters?", yes_no_dict],
                 12: ["What are your top reasons for buying leg quarters over other chicken/meat products?", yes_no_dict],
                 13: ["Do you prefer to purchase refrigerated or frozen leg quarters?", q13_dict],
                 14: ["Do you prefer to buy leg quarters in a bag, a tray, or from the meat counter?", q14_dict],
                 15: ["How do you store your leg quarters after you have purchased them?", yes_no_dict],
                 16: ["Do you typically use all of your leg quarters at one time or do you use a portion of them "\
                      "at one time?", q16_dict],
                 17: ["How do you prepare your leg quarters when you are getting ready to cook them?", yes_no_dict],
                 18: ["How do you cook your leg quarters?", yes_no_dict],
                 19: ["What time of day do you eat leg quarters?", yes_no_dict],
                 20: ["How many people do you typically prepare leg quarters for?", q20_dict],
                 22: ["If each of the following claims were added to the leg quarter you currently buy, would "\
                      "you be more or less likely to purchase this product?", q22_dict],
                 23: ["If each of the following claims were added to the leg quarter you currently buy, would "\
                      "you be willing to pay more or less to purchase this product?", q23_dict],
                 24: ["If the leg quarter product you currently buy were to come pre-seasoned, how likely "\
                      "would you be to purchase this product?", likeart_5_dict],
                 25: [" If each of the following pre-seasonings were added to the leg quarter you currently "\
                      "buy, would you be willing to pay more or less to purchase this product?", q23_dict]
                 }

# Declare file name    
file_name = "lq_survey_clean_data.xlsx"
        
# Import the excel as a pandas dataframe
df =  pd.read_excel(file_name)

# Initiate dictionary for location of questions within the dataframe
location_in_df_dict = {}

# Initiate a list for each question as matrix questions will have multiple columns
for question_num in question_dict:
    location_in_df_dict[question_num] = []

# Store the column names associated with each question for easy access later
# Then, using key defined above, change answer choices to numerical values
for question_num in question_dict:
    for col in df.columns:
        if question_dict[question_num][0] in col:
            location_in_df_dict[question_num].append(col)
            df[col].replace(question_dict[question_num][1], inplace=True)

# Function to resample data in order to calculate CI interval
def bootstrap_replicate_1d(data, func):
     bs_sample = pd.DataFrame(data = np.random.choice(data, len(data.index)))
     return func(bs_sample)

# Function that will perform the desired summary statistic depending on question type
def summary_statistics(df, column_name):
    
    # Create series from dataframe
    col = df[column_name]
    
    # Initalize list to hold output values
    output_list = np.zeros(19)
    
    # Calculate count for each answer choice
    count = col.value_counts()
    for i in count.index:
        output_list[i] = count[i]
    
    # Calculate % of total for each answer choice
    for i in range(0,8):
        output_list[i+8] = output_list[i] / np.sum(output_list[0:8])
    
    # Calculate the mean
    average = np.mean(col)
    output_list[16] = average
    
    # Compute the 95% confidence interval for the mean     
    resampled_data = np.empty(10000)
    for i in range(10000):
        resampled_data[i] = bootstrap_replicate_1d(col, np.mean)
    conf_int_95 = np.percentile(resampled_data, [2.5, 97.5])
    
    # Output ci to list
    output_list[17] = conf_int_95[0]
    output_list[18] =  conf_int_95[1]
         
    # Return the list containing summary statistics
    return output_list

def GetKey(val, dictionary):
    for key, value in dictionary.items():
        if val == value:
            return key
        else:
            return "NaN"

# Initalize columns
columns_summary_stats = ["0 Count", "1 Count", "2 Count", "3 Count", "4 Count", "5 Count", "6 Count", "7 Count",
                         "0 Percent", "1 Percent", "2 Percent", "3 Percent", "4 Percent", "5 Percent", "6 Percent", "7 Percent",
                         "Mean", "Conf_low", "Conf_high",
                         "0 Key", "1 Key", "2 Key", "3 Key", "4 Key", "5 Key",
                         "6 Key", "7 Key"]
# Create dataframe to house summary stats
df_summary_stats = pd.DataFrame(data=None, columns = columns_summary_stats)
# Initalize array for housing index information
index_array = [[],[],[]]

start_time = time.time()

# Write function that loops through our dictionary keys 
# and values sending them through our summary statistic function
def output_data(df, question_dict, location_in_df_dict):
    for quest_number in location_in_df_dict:
        for quest_text in location_in_df_dict[quest_number]:
            new_row = summary_statistics(df, quest_text) # Run summary stats function
            
            # In order to store information for what each number represents, we need to go from item to key in our choice dictionary
            choice_list = []
            keys = list(question_dict[quest_number][1].keys()) # Create list of keys
            vals = list(question_dict[quest_number][1].values()) # Create list of values
            # Loop over all possible integer values (0 to 7)
            for i in range(8):
                # Use a try statement to deal with errors
                try:
                    choice_list.append(keys[vals.index(i)]) # Use value to look up key, since key has the text
                except:
                    choice_list.append("NaN")
            # Turn into np array and concatenate for one np list object
            np_choice_list = np.array(choice_list) 
            new_row = np.concatenate((new_row, np_choice_list))
            
            df_summary_stats.loc[quest_text] = new_row # Add new row to dataframe
            index_array[0].append(quest_number) # Add question number to index array
            index_array[1].append(question_dict[quest_number][0]) # Add question text (cleaned) to index array
            
            # We want to pull out subquestions for matrix and 'select all' questions
            # To do so, we will write a regex that will identify the end of the string and see if text is there
            match = re.search(r"((\?  ){1}|(Select all that apply.){1}|(Choose up to three \(3\).){1}).+", quest_text)
            if match != None:
                values = match.group().rsplit("  ")
                index_array[2].append(values[1])
            else:
                index_array[2].append("NaN") # We'll set the index to NaN if there isn't anything  
        
        print("Elapsed time: ", ((time.time() - start_time) / 60))
        
    return df_summary_stats
    
# Run function that gives output data
output_df = output_data(df, question_dict, location_in_df_dict)

# Create index object and then add it to dataframe
index = pd.MultiIndex.from_arrays(index_array, names=("Question_number", "Question_text", "Question_option"))
output_df.set_index(index, inplace=True)      

# Export results to csv file
output_df.to_csv("lq_summary_stats_test_file.csv")             