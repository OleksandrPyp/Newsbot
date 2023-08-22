import json
import pandas as pd
import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from streamlit_lottie import st_lottie


def fetch_data(query):
    conn = sqlite3.connect('Final_project/bot_data.db')
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [description[0] for description in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    cursor.close()
    conn.close()
    return df


query_all = 'SELECT * FROM interactions'
df_all = fetch_data(query_all)

animation_path = "your animation path"
with open(animation_path, "r") as f:
    url = json.load(f)

st_lottie(url, speed=1, width=600, height=600, key="lottie_animation", loop=True, quality="high")

st.title('Bot Interactions Dashboard')
st.markdown('''
#### Summary:
This dashboard provides valuable insights into user interactions with the bot. You can analyze the data to understand 
user behavior, popular queries, and the effectiveness of different bot commands. The main objective is to use the visualizations to make data-driven 
decisions and improve the bots performance
''')

# General database stats
most_popular_command = df_all['command'].mode().values[0]
most_popular_language = df_all['language'].mode().values[0]
st.markdown(f'Most Popular Command: **{most_popular_command}**')
st.markdown(f'Most Popular Language: **{most_popular_language}**')

# Table with the bot interactions data
st.markdown('<br><br><br>', unsafe_allow_html=True)
st.subheader('Bot Interactions Database')
is_table_visible = st.checkbox('Show Table')
if is_table_visible:
    st.dataframe(df_all[['timestamp', 'query', 'command', 'username', 'language']])

# Wordcloud
filtered_df = df_all[df_all['query'].notnull()]
st.markdown('<br><br><br>', unsafe_allow_html=True)
st.subheader('Word Cloud: Queries')
st.markdown('''
The wordcloud visualizes the most commonly used queries by the users. Each word's size corresponds to its frequency in the queries.
The wordcloud helps to identify the popular topics that users are interested in
''')
st.markdown('<br><br>', unsafe_allow_html=True)
wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(' '.join(filtered_df['query']))
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
st.image(wordcloud.to_image())

query_command_count = '''
SELECT command, COUNT(*) as count
FROM interactions
GROUP BY command
'''
df = fetch_data(query_command_count)

# Commands used - pie chart
st.markdown('<br><br><br>', unsafe_allow_html=True)
st.subheader('Pie Chart: Used Commands')
st.markdown('''
The pie chart shows the distribution of used commands by the users. Each slice represents a different command, and the 
size of the slice corresponds to its usage frequency. The pie chart provides an overview of which commands are more 
frequently used by the users
''')
fig, ax = plt.subplots()
colors = ['#b4009e', '#dd6b7f', '#D9B300', '#B66DFF']
ax.pie(df['count'], labels=df['command'], autopct='%1.1f%%', startangle=90, colors=colors)
ax.set_aspect('equal')
st.pyplot(fig)

# Stacked column chart
st.subheader('Stacked Bar chart: Commands used')
st.markdown('''
The stacked bar chart displays the distribution of used commands over time. Each bar represents a specific date, and the 
height of each segment within the bar corresponds to the number of times a particular command was used on that date. 
The chart provides insights into the usage pattern of different commands on different days, allowing us to identify trends 
and patterns in the commands' frequency over time
''')
st.markdown('<br>', unsafe_allow_html=True)
df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
df_grouped = df_all.groupby([df_all['timestamp'].dt.date, 'command']).size().unstack(fill_value=0)
fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
df_grouped.plot(kind='bar', stacked=True, ax=ax_bar, color=colors)
ax_bar.set_xlabel('Date')
ax_bar.set_ylabel('Number of Commands')
ax_bar.set_xticklabels(pd.to_datetime(df_grouped.index).strftime('%Y-%m-%d'), rotation=45)
plt.tight_layout()
st.pyplot(fig_bar)
