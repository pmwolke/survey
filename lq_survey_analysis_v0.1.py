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
import seaborn as sns

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
    resampled_data = np.empty(1000)
    for i in range(1000):
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

columns_dtype = {"0 Count" : "float", "1 Count": "float", "2 Count": "float", "3 Count": "float", "4 Count": "float", "5 Count": "float",
                "6 Count": "float", "7 Count": "float", "0 Percent": "float", "1 Percent": "float", "2 Percent": "float",
                "3 Percent": "float", "4 Percent": "float", "5 Percent": "float", "6 Percent": "float", "7 Percent": "float",
                "Mean": "float", "Conf_low": "float", "Conf_high": "float", "0 Key": "str", "1 Key": "str", "2 Key": "str",
                "3 Key": "str", "4 Key": "str", "5 Key": "str", "6 Key": "str", "7 Key": "str"}

start_time = time.time()

# Write function that loops through our dictionary keys 
# and values sending them through our summary statistic function
def output_data(df, question_dict, location_in_df_dict):
    
    # Create dataframe to house summary stats
    df_summary_stats = pd.DataFrame(data=None, columns = columns_summary_stats)
    # Initalize array for housing index information
    index_array = [[],[],[]]
    
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
    
    # We need to ensure data type is what we want or expect for each column    
    for col in df_summary_stats.columns:
        type = columns_dtype[col]
        df_summary_stats[col] = df_summary_stats[col].astype(type)
    
    # Create index object and then add it to dataframe
    index = index = pd.MultiIndex.from_arrays(index_array, names=("Question_number", "Question_text", "Question_option"))
    df_summary_stats.set_index(index, inplace=True)
    
    print("Dataframe output complete", round((time.time() - start_time)/60, 2), "mins")
    
    return df_summary_stats, index_array[2]

# Run function that gives output of all data with no segmentations
output_df, _ = output_data(df, question_dict, location_in_df_dict)

# We want to segment by question one in the survey
i=0
with pd.ExcelWriter("summary_stats_output_by_store.xlsx") as writer:
    for question in location_in_df_dict[1]:
        yes_filter = df[df[question] == 1] # 1 is yes, they shop at this store
        no_filter = df[df[question] == 0] # 0 is no, they don't shop at this store
        
        # Get summary stats for both yes and no
        yes_output, store = output_data(yes_filter, question_dict, location_in_df_dict)
        no_output, _ = output_data(no_filter, question_dict, location_in_df_dict)
        
        # Look at difference in mean for both respondents that don't shop at that store and the total
        yes_output["Difference_in_mean_from_nonshopper"] = yes_output["Mean"] - no_output["Mean"]
        yes_output["Difference_in_mean_from_total"] = yes_output["Mean"] - output_df["Mean"]
        
        # Need conditions for our column indicating if there is a meaningful difference in average
        conditions_1 = [
            (yes_output["Mean"] < no_output["Conf_low"]),
            (yes_output["Mean"] > no_output["Conf_high"])
             ]
        
        conditions_2 = [
            (yes_output["Mean"] < output_df["Conf_low"]),
            (yes_output["Mean"] > output_df["Conf_high"])
             ]
        
        choices = ["Mean is meaningfully lower", "Mean is meaningfully higher"] # Choices depending on conditions above
        
        # Create new columns we can quickly identify if there is a difference
        yes_output["Meaningfully different from nonshopper"] = np.select(conditions_1, choices, default = "Not meaningfully different")
        yes_output["Meaningfully different from total"] = np.select(conditions_2, choices, default = "Not meaningfully different")
        
        # Send data to excel file, with it's unqiue sheet
        yes_output.to_excel(writer, sheet_name = store[i][:20], merge_cells=False)
        
        i += 1 # i is just a counter (the writer is still learning python and understands this is not ideal)

with pd.ExcelWriter("summary_stats_output_by_q14.xlsx") as writer:
    question_14_text = location_in_df_dict[14][0]
    bag_pref = df[df[question_14_text] == 1]
    tray_pref = df[df[question_14_text] == 2]
    counter_pref = df[df[question_14_text] == 3]
    no_pref = df[df[question_14_text] == 4]
    
    bag_pref_output, _ = output_data(bag_pref, question_dict, location_in_df_dict)
    tray_pref_output, _ = output_data(tray_pref, question_dict, location_in_df_dict)
    counter_pref_output, _ = output_data(counter_pref, question_dict, location_in_df_dict)
    no_pref_output, _ = output_data(no_pref, question_dict, location_in_df_dict)
    
    bag_pref_output.to_excel(writer, sheet_name="Bag", merge_cells=False)
    tray_pref_output.to_excel(writer, sheet_name="Tray", merge_cells=False)
    counter_pref_output.to_excel(writer, sheet_name="Counter", merge_cells=False)
    no_pref_output.to_excel(writer, sheet_name="None", merge_cells=False)
    
i=0
with pd.ExcelWriter("summary_stats_output_by_q19.xlsx") as writer:
    for question in location_in_df_dict[19]:
        yes_filter = df[df[question] == 1] # 1 is yes, they eat lqs at this time of day
        no_filter = df[df[question] == 0]
        
        yes_output, time_of_day = output_data(yes_filter, question_dict, location_in_df_dict)
        no_output, _ = output_data(no_filter, question_dict, location_in_df_dict)
        
        yes_output["Difference_in_mean_from_nonshopper"] = yes_output["Mean"] - no_output["Mean"]
        yes_output["Difference_in_mean_from_total"] = yes_output["Mean"] - output_df["Mean"]
        
        # Need conditions for our column indicating if there is a meaningful difference in average
        conditions_1 = [
            (yes_output["Mean"] < no_output["Conf_low"]),
            (yes_output["Mean"] > no_output["Conf_high"])
             ]
        
        conditions_2 = [
            (yes_output["Mean"] < output_df["Conf_low"]),
            (yes_output["Mean"] > output_df["Conf_high"])
             ]
        
        choices = ["Mean is meaningfully lower", "Mean is meaningfully higher"] # Choices depending on conditions above
        
        # Create new columns we can quickly identify if there is a difference
        yes_output["Meaningfully different from nonshopper"] = np.select(conditions_1, choices, default = "Not meaningfully different")
        yes_output["Meaningfully different from total"] = np.select(conditions_2, choices, default = "Not meaningfully different")
        
        # Send data to excel file, with it's unqiue sheet
        yes_output.to_excel(writer, sheet_name = str(i), merge_cells=False)
        
        i += 1

with pd.ExcelWriter("summary_stats_output_by_q20.xlsx") as writer:
    question_14_text = location_in_df_dict[20][0]
    cook_for_1 = df[df[question_14_text] == 1]
    cook_for_2 = df[df[question_14_text] == 2]
    cook_for_3 = df[df[question_14_text] == 3]
    cook_for_4 = df[df[question_14_text] == 4]
    cook_for_5 = df[df[question_14_text] == 5]
    
    cook_for_1_output, _ = output_data(cook_for_1, question_dict, location_in_df_dict)
    cook_for_2_output, _ = output_data(cook_for_2, question_dict, location_in_df_dict)
    cook_for_3_output, _ = output_data(cook_for_3, question_dict, location_in_df_dict)
    cook_for_4_output, _ = output_data(cook_for_4, question_dict, location_in_df_dict)
    cook_for_5_output, _ = output_data(cook_for_5, question_dict, location_in_df_dict)
    
    cook_for_1_output.to_excel(writer, sheet_name="1", merge_cells=False)
    cook_for_2_output.to_excel(writer, sheet_name="2", merge_cells=False)
    cook_for_3_output.to_excel(writer, sheet_name="3", merge_cells=False)
    cook_for_4_output.to_excel(writer, sheet_name="4", merge_cells=False)
    cook_for_5_output.to_excel(writer, sheet_name="5", merge_cells=False)

# output_df.reset_index(level=[1,2], inplace=True)
# test_x = "Question_option"
# sns_plot = sns.barplot(x = test_x, y = "1 Count", data=output_df.loc[1].sort_values(by=["1 Count"], ascending=False), palette="mako")
# sns_plot.set_xticklabels(sns_plot.get_xticklabels(), rotation=90)
# plt.title(question_dict[1][0])
# plt.savefig("test_fig.png", transparent=True, format="png", dpi=200)
    
# Export results to our excel file in it's own sheet
with pd.ExcelWriter("summary_stats_output_total.xlsx") as writer:
    output_df.to_excel(writer, sheet_name = "All respondents", merge_cells=False)             