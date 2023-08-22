import pandas as pd
import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
from wordcloud import WordCloud

conn = sqlite3.connect('Final_project/bot_data.db')
cursor = conn.cursor()

query = 'SELECT * FROM interactions'
cursor.execute(query)

columns = [description[0] for description in cursor.description]
data = cursor.fetchall()
df = pd.DataFrame(data, columns=columns)
cursor.close()
conn.close()

command_counts = df['command'].value_counts()
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

st.title('Bot Interactions Dashboard')

# Table with the bot interactions data
st.subheader('Bot Interactions Data')
st.table(df[['timestamp', 'query', 'command', 'username', 'language']])

# Wordcloud
st.subheader('Word Cloud: Queries')
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df['query']))
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
st.image(wordcloud.to_image())

# Commands used - pie chart
st.subheader('Pie Chart: Used Commands')
fig, ax = plt.subplots()
ax.pie(df['count'], labels=df['command'], autopct='%1.1f%%', startangle=90)
ax.set_aspect('equal')
st.pyplot(fig)
