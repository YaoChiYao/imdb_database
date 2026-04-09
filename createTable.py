import pandas as pd
import sqlite3

class Create_Table:
    def __init__(self):
        self.df = pd.read_csv("imdb_top_1000.csv")

    #清理数据
    def data_clean(self):
        self.df['Released_Year'] = pd.to_numeric(self.df['Released_Year'], errors='coerce')
        self.df = self.df.dropna(subset=['Released_Year'])
        self.df['Released_Year'] = self.df['Released_Year'].astype(int)
        self.df['Runtime'] = self.df['Runtime'].str.replace(' min', '')
        self.df['Runtime'] = pd.to_numeric(self.df['Runtime'], errors='coerce')
        self.df['Gross'] = self.df['Gross'].str.replace(',', '')
        self.df['Gross'] = pd.to_numeric(self.df['Gross'], errors='coerce') 

    #建表
    def build_table(self):
        self.director_table = self.df[['Director']].drop_duplicates().reset_index(drop=True)
        self.director_table['director_id'] = self.director_table.index + 1

        actors = pd.concat([self.df['Star1'], self.df['Star2'], self.df['Star3'], self.df['Star4']])
        self.actor_table = pd.DataFrame(actors.unique(), columns=['actor_name'])
        self.actor_table['actor_id'] = self.actor_table.index + 1

        self.df['Genre'] = self.df['Genre'].str.split(', ')
        genre_exploded = self.df.explode('Genre')
        self.genre_table = pd.DataFrame(genre_exploded['Genre'].unique(), columns=['genre'])
        self.genre_table['genre_id'] = self.genre_table.index + 1

        self.df = self.df.merge(self.director_table, on='Director')
        self.movie_table = self.df[[
            'Series_Title', 'Released_Year', 'Certificate', 'Runtime',
            'IMDB_Rating', 'Meta_score', 'No_of_Votes', 'Gross',
            'Overview', 'Poster_Link', 'director_id'
        ]].copy()
        self.movie_table = self.movie_table.reset_index(drop=True)
        self.movie_table['movie_id'] = self.movie_table.index + 1

        #建立关系表
        movie_actor_list = []
        for _, row in self.df.iterrows():
            movie_id = self.movie_table.loc[self.movie_table['Series_Title'] == row['Series_Title'], 'movie_id'].values[0]
            for star in ['Star1', 'Star2', 'Star3', 'Star4']:
                actor_id = self.actor_table.loc[self.actor_table['actor_name'] == row[star], 'actor_id'].values[0]
                movie_actor_list.append((movie_id, actor_id))
        self.movie_actor_table = pd.DataFrame(movie_actor_list, columns=['movie_id', 'actor_id']).drop_duplicates()

        movie_genre_list = []
        for _, row in genre_exploded.iterrows():
            movie_id = self.movie_table.loc[self.movie_table['Series_Title'] == row['Series_Title'], 'movie_id'].values[0]
            genre_id = self.genre_table.loc[self.genre_table['genre'] == row['Genre'], 'genre_id'].values[0]
            movie_genre_list.append((movie_id, genre_id))
        self.movie_genre_table = pd.DataFrame(movie_genre_list, columns=['movie_id', 'genre_id']).drop_duplicates()

    #写入sql
    def write(self):
        conn = sqlite3.connect("movies.db")
        cur = conn.cursor()
        cur.executescript("""
            DROP TABLE IF EXISTS Movie;
            DROP TABLE IF EXISTS Director;
            DROP TABLE IF EXISTS Actor;
            DROP TABLE IF EXISTS Genre;
            DROP TABLE IF EXISTS Movie_Actor;
            DROP TABLE IF EXISTS Movie_Genre;
            """)
        cur.executescript("""
            CREATE TABLE Director (
                director_id INTEGER PRIMARY KEY,
                director_name TEXT
            );

            CREATE TABLE Actor (
                actor_id INTEGER PRIMARY KEY,
                actor_name TEXT
            );              
                          
            CREATE TABLE Genre (
                genre_id INTEGER PRIMARY KEY,
                genre TEXT
            ); 

            CREATE TABLE Movie (
                movie_id INTEGER PRIMARY KEY,
                title TEXT,
                year INTEGER,
                certificate TEXT,
                runtime INTEGER,
                imdb_rating REAL,
                meta_score REAL,
                votes INTEGER,
                gross REAL,
                overview TEXT,
                poster_link TEXT,
                director_id INTEGER,
                FOREIGN KEY (director_id) REFERENCES Director(director_id)
            ); 

            CREATE TABLE Movie_Actor (
                movie_id INTEGER,
                actor_id INTEGER,
                PRIMARY KEY (movie_id, actor_id),
                FOREIGN KEY (movie_id) REFERENCES Movie(movie_id),
                FOREIGN KEY (actor_id) REFERENCES Actor(actor_id)
            );
            
            CREATE TABLE Movie_Genre (
                movie_id INTEGER,
                genre_id INTEGER,
                PRIMARY KEY (movie_id, genre_id),
                FOREIGN KEY (movie_id) REFERENCES Movie(movie_id),
                FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
            );
                          
            """)
        self.director_table.rename(columns={'Director': 'director_name'}, inplace=True)
        self.director_table.to_sql('Director', conn, if_exists='append', index=False)
        self.actor_table.to_sql('Actor', conn, if_exists='append', index=False)
        self.genre_table.to_sql('Genre', conn, if_exists='append', index=False)
        self.movie_table.rename(columns={
            'Series_Title': 'title',
            'Released_Year': 'year',
            'IMDB_Rating': 'imdb_rating',
            'Meta_score': 'meta_score',
            'No_of_Votes': 'votes',
            'Poster_Link': 'poster_link'
        }, inplace=True)
        self.movie_table.to_sql('Movie', conn, if_exists='append', index=False)
        self.movie_actor_table.to_sql('Movie_Actor', conn, if_exists='append', index=False)
        self.movie_genre_table.to_sql('Movie_Genre', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
