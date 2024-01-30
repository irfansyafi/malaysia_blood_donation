# malaysia_blood_donation
This is the repo for blood donation that I obtain from https://github.com/MoH-Malaysia
Can adapt this code to your bot, insert your own telegram TOKEN API KEY and CHAT_ID into your own .env file.

Working files ?
1. analytics_script.py
2. telegrambot_v3.py

How this repo work?

1. Run the telegrambot_v3.py script then the code will use the analytics_script.py
2. The telegram will be active. The telegrambot will save the image of the plot into local folder (graph_pic)
3. The telegram bot are already added in the Malaysia Blood Analytics. You can add it into your own group.
4. Send command through the group /start and /plot.
5. The telegrambot_v3.py script will send 3 plot on:
   - Total blood donation retention based on age categories (This may due to campaign done by company to encourage blood donation. Hence, why most of the age between 30-34 (Working adults) donates more than others.
   - The trend of blood donation from 2019-2024 for each states in Malaysia (Monthly)
   - The trend of blood_type over time.
6. Everyday, at around 8-10 am there will be updated from the sources. The script might be run on windows scheduler around 8-10 am

Future work recommendation:
1. Explore on the usage of duckdb for managing multiple data sources instead of a csv file.
2. Explore on the usage of cloud computing to leveraging Data Lake and Data Warehouse.
3. Automation process where the code will run if there is changes from the data source. Currently, we can run daily and changes made will store in a csv file to save credit from using Cloud Computing services.
4. More analysis that can done that would improve and help decision-maker.
   For example:
   1) Which facilities or hospital that have lesser people donating blood?
   2) Seasonal analysis regarding blood donation. When do people always go out for blood donation?
   3) Which facilities that have no blood donation? Is it because there is no facilities provided for the hospital to conduct blood transfer from donators?
