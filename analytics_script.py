import pandas as pd
import logging
import os
import matplotlib.pyplot as plt
logging.getLogger().setLevel(logging.INFO)

donation_facilities_url = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_facility.csv"
donation_state_url = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_state.csv"
newdonors_facility_url = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/newdonors_facility.csv"
newdonors_state_url = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/newdonors_state.csv"

# Get data from the url
def get_data_url(url_link):
    try:
        data = pd.read_csv(url_link) # , parse_dates=['date'], index_col='date'
        logging.info(f"Getting data from {url_link}")
        return data
    except Exception as e:
        logging.error(f"Unexpected error fetching data from {url_link}: {e}")
        return None

donation_facilities = get_data_url(donation_facilities_url)
donation_state = get_data_url(donation_state_url)
newdonors_facility = get_data_url(newdonors_facility_url)
newdonors_state = get_data_url(newdonors_state_url)

blood_donation_retention = pd.read_parquet("https://dub.sh/ds-data-granular") # In this parquet, there is no date


# Append data into new csv file
def append_data(data, file_path):
    if os.path.exists(file_path):
        existing_data = pd.read_csv(file_path)
        updated_data = pd.merge(existing_data, data, how='outer', indicator=True).query('_merge == "right_only"').drop('_merge', axis=1)
    else:
        updated_data = data
        logging.info(f"File not exist. Create new file")

    updated_data.to_csv(file_path, index=False, mode='a', header=not os.path.exists(file_path))
    logging.info(f"Data appended to {file_path}.")

    return pd.read_csv(file_path)

donation_facilities_updated = append_data(donation_facilities, "donation_facilities.csv")
donation_state_updated = append_data(donation_state, "donation_state.csv")
newdonors_facility_updated = append_data(newdonors_facility,"newdonors_facility.csv")
newdonors_state_updated = append_data(newdonors_state, "newdonors_state.csv")
blood_donation_retention_updated = append_data(blood_donation_retention, "blood_donation_retention.csv")

# Change date time to datetimeindex
def change_dataframe_timeindex(dataframe):
    dataframe['date'] = pd.to_datetime(dataframe['date'],errors='coerce')
    dataframe = dataframe.set_index('date', inplace=True)


change_dataframe_timeindex(donation_facilities_updated)
change_dataframe_timeindex(donation_state_updated)
change_dataframe_timeindex(newdonors_facility_updated)
change_dataframe_timeindex(newdonors_state_updated)


# Transform data and visualization for yearly total donation on each blood type

oldest_date = donation_state_updated.index.min()
newest_date = donation_state_updated.index.max()
print(oldest_date)
print(newest_date)

donation_state_updated_resampled = donation_state_updated.resample('Y').sum()
donation_state_updated_resampled = donation_state_updated_resampled.loc[oldest_date:newest_date]

donation_state_updated_resampled['blood_a'].plot(label='Blood Type A', color='red')
donation_state_updated_resampled['blood_ab'].plot(label='Blood Type AB', color='green')
donation_state_updated_resampled['blood_b'].plot(label='Blood Type B', color='blue')
donation_state_updated_resampled['blood_o'].plot(label='Blood Type O', color='orange')

plt.title("Yearly Blood Donation Trends")
plt.xlabel("Year")
plt.ylabel("Total Blood Donation Count")
plt.legend()
plt.show()

# Plotting graph for the states trend from 2019 - 2024 
column_used = ['state','total']
newdf = newdonors_state_updated[column_used]
latest_date = newdf.index.max()
from_date = '2019-01'

sliced_newdf = newdf[(newdf.index >= from_date) & (newdf.index <= latest_date)]

grouped_sliced_newdf = sliced_newdf.groupby(['state', pd.Grouper(freq='M')])['total'].sum().reset_index()
grouped_sliced_newdf.set_index(grouped_sliced_newdf['date'],inplace=True)

state_in_malaysia = grouped_sliced_newdf['state'].unique()
state_in_malaysia = list(state_in_malaysia)
state_in_malaysia.remove('Malaysia')
print(state_in_malaysia)

pivoted_grouped_sliced_newdf = grouped_sliced_newdf.pivot(columns='state', values='total')
print(pivoted_grouped_sliced_newdf)

yesterday_data = pivoted_grouped_sliced_newdf.iloc[-2]
today_data = pivoted_grouped_sliced_newdf.iloc[-1]
change_data = today_data - yesterday_data

messages = ""
for state, change in change_data.items():
    messages += f"{state}: {change}\n"

fig, ax = plt.subplots(figsize=(12, 8))
for state in state_in_malaysia:
    pivoted_grouped_sliced_newdf[state].plot(marker='o', label=state)


ax.set_title("Monthly Blood Donation Trends by State (2019-2023)")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Donations")
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()


# Plotting graph for total blood donation based on age category. Assumption of which age category that always come back to donate can be deduce.
blood_donation_retention_updated['age'] = int(newest_date.year) - blood_donation_retention_updated['birth_date']
plt.figure(figsize=(16,8))
idcount = blood_donation_retention_updated['donor_id'].value_counts()
oldest = blood_donation_retention_updated['birth_date'].min()
youngest = blood_donation_retention_updated['birth_date'].max()
age_group_list = newdonors_state_updated.columns[1:11].to_list()
print(age_group_list)
print(oldest)
print(youngest)

bins = [16, 24, 29, 34, 39, 44, 49, 54, 59, 64, 150]


blood_donation_retention_updated['age_group'] = pd.cut(blood_donation_retention_updated['age'], bins=bins, labels=age_group_list, right=False)

blood_donation_grouped = blood_donation_retention_updated.groupby(by=['age_group']).count()


fig, ax = plt.subplots()
ax.bar(blood_donation_grouped.index,pd.to_numeric(blood_donation_grouped['age']))
ax.set_title("Total blood donation retention based on Age Categories ")
ax.set_xlabel("Age Categories")
ax.set_ylabel('Total Donation by Millions')
plt.show()


# Average of retention for blood donation per person

donor_grouped = blood_donation_retention_updated.groupby(by = ['donor_id']).count()
donor_grouped.head(10)
average_per_person = donor_grouped['visit_date'].mean()
print(average_per_person)

print("Running Completed")
