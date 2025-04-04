# -*- coding: utf-8 -*-
"""notebook.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pig64r4cr-mc5hEHCY5kUfCd8Zo3wpH2

# Spotify Song Recommendations - Muchammad Wildan Alkautsar

## Import Library
"""

import numpy as np
import pandas as pd
import zipfile
import warnings
warnings.filterwarnings('ignore')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score

"""Library which will be used for project

## Loading the Data
"""

with zipfile.ZipFile("Spotify.zip", "r") as z:
    file_list = z.namelist()

print("List file in the ZIP:", file_list)

with zipfile.ZipFile("Spotify.zip", "r") as z:
    with z.open("top10s.csv") as f:
        df = pd.read_csv(f, encoding='latin1')

# Show first 5 rows
df.head().set_index('Unnamed: 0')

"""Open first 5 Rows

## Univariate Exploratory Data Analysis
"""

df.info()

"""Information about data

Data dictionary

- **title**: The title of the song  
- **artist**: The artist of the song  
- **top genre**: The genre of the song  
- **year**: The year the song was in the Billboard  
- **bpm**: Beats per minute - the tempo of the song  
- **nrgy**: The energy of the song - higher values mean more energetic (fast, loud)  
- **dnce**: The danceability of the song - higher values mean it's easier to dance to  
- **dB**: Decibel - the loudness of the song  
- **live**: Liveness - likeliness the song was recorded with a live audience  
- **val**: Valence - higher values mean a more positive sound (happy, cheerful)  
- **dur**: The duration of the song  
- **acous**: The acousticness of the song - likeliness the song is acoustic  
- **spch**: Speechiness - higher values mean more spoken words  
- **pop**: Popularity - higher values mean more popular  
"""

df.describe()

"""Show the descriptif statistics of the data

"""

len(df)

"""number of lines

## Data Preprocessing
"""

df.isna().sum()

"""No have a missing values in the data"""

df.duplicated().sum()

"""No have a duplicates values in the data

## Data Preparation
"""

df['top genre'].unique()

"""df['top genre'].unique() returns an array of unique genre names present in the "top genre" column of the dataset."""

df = df[['title', 'top genre']]

"""Because to make a recomendation game base on genre, we only need title and genre features"""

df

from sklearn.feature_extraction.text import TfidfVectorizer

tf = TfidfVectorizer()

# Melakukan fit lalu ditransformasikan ke bentuk matrix
tfidf_matrix = tf.fit_transform(df['top genre'])

# Melihat ukuran matrix tfidf
tfidf_matrix.shape

"""The code uses TfidfVectorizer() to convert the "top genre" column into a TF-IDF matrix. The tfidf_matrix.shape command then returns the dimensions of the resulting matrix, showing the number of rows (songs) and columns (unique genre terms).

## Model Development dengan Content Based Filtering
"""

df_tfidf = pd.DataFrame(
    tfidf_matrix.toarray(),
    columns=tf.get_feature_names_out(),  # Pakai vectorizer
    index=df.title
)

# Cek jumlah fitur dan game yang tersedia
num_features = df_tfidf.shape[1]
num_games = df_tfidf.shape[0]

# Ambil sampel dengan jumlah yang valid
df_tfidf.sample(min(22, num_features), axis=1).sample(min(10, num_games), axis=0)

"""The code converts the TF-IDF matrix into a Pandas DataFrame, where the rows represent song titles and the columns represent unique genre terms extracted by the vectorizer. It then calculates the number of features (num_features) and the number of songs (num_games) in the dataset. Finally, it selects a random subset of up to 22 features and 10 songs to sample for inspection."""

from sklearn.metrics.pairwise import cosine_similarity

# Menghitung cosine similarity pada matrix tf-idf
cosine_sim = cosine_similarity(tfidf_matrix)
cosine_sim

"""TF-IDF (Term Frequency-Inverse Document Frequency) Vectorization is a technique in Natural Language Processing (NLP) that converts text into numerical representations by considering both the frequency of a term in a document (Term Frequency) and how unique that term is across the entire corpus (Inverse Document Frequency). In the code above, TfidfVectorizer() is used to transform the genre column from df_train["genre"] into a TF-IDF-based feature matrix. The fit_transform() method first learns the text characteristics (by tokenizing and computing TF-IDF values for each term) and then converts the data into a sparse matrix. This matrix can be used in machine learning models for tasks such as text classification or content-based recommendation systems.

Cosine similarity is a metric used to measure the similarity between two vectors by calculating the cosine of the angle between them. In the code above, cosine_similarity(tfidf_matrix, tfidf_matrix) computes the pairwise cosine similarity between all genre representations in tfidf_matrix. Since tfidf_matrix is a numerical representation of text data, this operation results in a similarity matrix where each entry (i, j) represents the similarity between the i-th and j-th game genres. A value close to 1 indicates high similarity, while a value close to 0 means low similarity. This technique is commonly used in content-based recommendation systems to find items with similar characteristics.
"""

def song_recommendations(title, similarity_data=cosine_sim, items=df, k=5):
    indices = pd.Series(df.index, index=df["title"]).drop_duplicates()

    if title not in indices:
        return f"Judul '{title}' tidak ditemukan dalam dataset."

    idx = indices[title]
    sim_scores = list(enumerate(similarity_data[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:k+1]
    song_indices = [i[0] for i in sim_scores]

    return df.iloc[song_indices][["title", "top genre"]]

"""The song_recommendations() function recommends songs based on genre similarity using cosine similarity. First, it creates a Series containing song indices with their titles as the index, ensuring uniqueness by removing duplicates. If the given title is not found in the dataset, the function returns an error message. Next, it retrieves the song's index, calculates its cosine similarity with all other songs, and sorts the results in descending order. The top five most similar songs (excluding the input song itself) are selected as recommendations. Finally, the function returns a list of recommended songs, including their titles and genres, from the dataset.








"""

recommendations = song_recommendations("Broken Arrows", k=3)
print(recommendations)

"""The function song_recommendations("Broken Arrows", k=3) retrieves three songs with the highest cosine similarity to "Broken Arrows" based on genre. The output displays a DataFrame containing the recommended songs along with their genres. This ensures that the recommendations are closely related to the input song in terms of musical style.

## Evaluation
"""

def calculate_precision(title, recommendations):
    if recommendations.empty:
        return 0.0

    song_genre = df[df["title"] == title]["top genre"].values[0]
    relevant_recommendations = sum(recommendations["top genre"] == song_genre)

    precision = relevant_recommendations / len(recommendations)
    return precision

"""The calculate_precision() function measures the accuracy of song recommendations by calculating precision. It first checks if the recommendations list is empty; if so, it returns 0.0. Then, it retrieves the genre of the input song and counts how many recommended songs share the same genre. Precision is computed as the ratio of relevant recommendations (same genre) to the total number of recommendations. A higher precision value indicates that the recommendation system is more effective in suggesting songs with similar genres."""

# Example Using
title_input = "Broken Arrows"
recommendations = song_recommendations(title_input, k=5)
precision_score = calculate_precision(title_input, recommendations)

print("Recomendation Song:")
print(recommendations)
print(f"\nPrecision: {precision_score:.2f}")

"""The code snippet demonstrates how to use the song recommendation system and evaluate its precision. First, it sets "Broken Arrows" as the input title and retrieves five recommended songs using the song_recommendations() function. Then, it calculates the precision score by comparing the genres of the recommendations with the input song's genre using calculate_precision(). Finally, it prints the recommended songs along with their genres and displays the precision score, formatted to two decimal places, indicating the effectiveness of the recommendation system.

The output shows that all five recommended songs belong to the same genre as the input song, "Broken Arrows", which is "big room". Since every recommended song matches the input song's genre, the precision score is 1.00 (100%), indicating a perfect recommendation accuracy. This means the recommendation system is highly effective in suggesting songs within the same genre.
"""