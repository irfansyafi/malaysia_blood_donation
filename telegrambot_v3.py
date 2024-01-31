import telebot
import os
import matplotlib.pyplot as plt
import pandas as pd
from analytics_script import blood_donation_grouped, donation_state_updated_resampled, average_per_person,state_in_malaysia,pivoted_grouped_sliced_newdf,messages
from io import BytesIO
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
GRAPH_PIC_FOLDER = "graph_pic"
bot_ = telebot.TeleBot(TOKEN)


@bot_.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot_.reply_to(message, "Send /plot to get today's graph")


@bot_.message_handler(commands=['plot'])
def analytic_graph(message):
    try:
        timestamp = datetime.now().strftime("%Y%m%d")

        try:
            # For Blood Retention based on Age Categories
            fig, ax = plt.subplots()
            ax.bar(blood_donation_grouped.index, pd.to_numeric(blood_donation_grouped['age']))
            ax.set_title("Total blood donation retention based on Age Categories ")
            ax.set_xlabel("Age Categories")
            ax.set_ylabel('Total Donation by Millions')

            filename_age_category = f'donation_age_{timestamp}.png'
            filepath_age_category = os.path.join(GRAPH_PIC_FOLDER, filename_age_category)

            plt.savefig(filepath_age_category, format='png', facecolor='white')
            plt.clf()

            bot_.send_message(CHAT_ID, "This is the total donation retention based on age category")
            with open(filepath_age_category, 'rb') as age_photo:
                bot_.send_photo(CHAT_ID, age_photo)

            # For States trend (Monthly)
            fig, ax = plt.subplots()
            for state in state_in_malaysia:
                pivoted_grouped_sliced_newdf[state].plot(marker='o', label=state)

            ax.set_title("Monthly Blood Donation Trends by State (2019-2023)")
            ax.set_xlabel("Year")
            ax.set_ylabel("Number of Donations")
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')            
            
            filename_state_trend = f'state_trend_monthly_{timestamp}.png'
            filepath_state_trend = os.path.join(GRAPH_PIC_FOLDER, filename_state_trend)

            plt.savefig(filepath_state_trend, format='png', bbox_inches='tight', facecolor='white')
            plt.clf()

            bot_.send_message(CHAT_ID, "This is the for every state in Malaysia from 2019 till today (Monthly)")
            with open(filepath_state_trend, 'rb') as statetrend_photo:
                bot_.send_photo(CHAT_ID, statetrend_photo)
            bot_.send_message(CHAT_ID, "CHANGES OF THE DATA FROM YESTERDAY")
            bot_.send_message(CHAT_ID, messages)

            # For blood type trend
            fig, ax = plt.subplots()
            donation_state_updated_resampled['blood_a'].plot(label='Blood Type A', color='red')
            donation_state_updated_resampled['blood_ab'].plot(label='Blood Type AB', color='green')
            donation_state_updated_resampled['blood_b'].plot(label='Blood Type B', color='blue')
            donation_state_updated_resampled['blood_o'].plot(label='Blood Type O', color='orange')

            plt.title("Yearly Blood Donation Trends")
            plt.xlabel("Year")
            plt.ylabel("Total Blood Donation Count")
            plt.legend()

            filename_blood_types = f'blood_types_{timestamp}.png'
            filepath_blood_types = os.path.join(GRAPH_PIC_FOLDER, filename_blood_types)

            plt.savefig(filepath_blood_types, format='png', facecolor='white')
            plt.clf() 

            bot_.send_message(CHAT_ID, "This is the trend throughout the years till this date for each blood type")
            with open(filepath_blood_types, 'rb') as blood_type_photo:
                bot_.send_photo(CHAT_ID, blood_type_photo)

            plt.close()

            bot_.send_message(CHAT_ID, f"An average person donates at least {round(average_per_person)} times throughout their life")
        except Exception as e:
            bot_.send_message(CHAT_ID, f"An error occurred: {str(e)}")

    except telebot.apihelper.ApiTelegramException as e:
        if "Bad Request: chat not found" in str(e):
            bot_.send_message(CHAT_ID, "Error: Chat not found. Please start a conversation first.")


if __name__ == "__main__":
    bot_.polling()
