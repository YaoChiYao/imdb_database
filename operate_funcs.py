import mysql.connector
import pandas as pd
from contextlib import contextmanager


class MovieDatabase:
    def __init__(self, host='localhost', user='root', password='password', database='movies_db'):
        """初始化数据库连接"""
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.conn = mysql.connector.connect(**self.config)
        self.cursor = self.conn.cursor(dictionary=True)
    
    # ==================== 连接管理 ====================
    
    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def commit(self):
        """提交事务"""
        self.conn.commit()
    
    def rollback(self):
        """回滚事务"""
        self.conn.rollback()

    # ==================== Movie 表操作 ====================
    
    # 1. 查询函数
    def get_all_movies(self, limit=None, offset=0):
        """获取所有电影列表"""
        query = "SELECT * FROM Movie ORDER BY imdb_rating DESC"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_movie_by_id(self, movie_id):
        """根据ID查询电影详情"""
        query = "SELECT * FROM Movie WHERE movie_id = %s"
        self.cursor.execute(query, (movie_id,))
        return self.cursor.fetchone()
    
    def get_movies_by_director(self, director_name):
        """查询某个导演的所有电影"""
        query = """
        SELECT m.*, d.director_name
        FROM Movie m
        JOIN Director d ON m.director_id = d.director_id
        WHERE d.director_name = %s
        ORDER BY m.imdb_rating DESC
        """
        self.cursor.execute(query, (director_name,))
        return self.cursor.fetchall()
    
    def get_movies_by_actor(self, actor_name):
        """查询某个演员参演的所有电影"""
        query = """
        SELECT m.*, a.actor_name
        FROM Movie m
        JOIN Movie_Actor ma ON m.movie_id = ma.movie_id
        JOIN Actor a ON ma.actor_id = a.actor_id
        WHERE a.actor_name = %s
        ORDER BY m.imdb_rating DESC
        """
        self.cursor.execute(query, (actor_name,))
        return self.cursor.fetchall()
    
    def get_movies_by_genre(self, genre):
        """查询某个类型的所有电影"""
        query = """
        SELECT m.*, g.genre
        FROM Movie m
        JOIN Movie_Genre mg ON m.movie_id = mg.movie_id
        JOIN Genre g ON mg.genre_id = g.genre_id
        WHERE g.genre = %s
        ORDER BY m.imdb_rating DESC
        """
        self.cursor.execute(query, (genre,))
        return self.cursor.fetchall()
    
    def get_movies_by_year(self, year):
        """查询某年发布的所有电影"""
        query = """
        SELECT * FROM Movie 
        WHERE year = %s
        ORDER BY imdb_rating DESC
        """
        self.cursor.execute(query, (year,))
        return self.cursor.fetchall()
    
    def get_movies_by_year_range(self, start_year, end_year):
        """查询某个年份范围内的电影"""
        query = """
        SELECT * FROM Movie 
        WHERE year BETWEEN %s AND %s
        ORDER BY year DESC, imdb_rating DESC
        """
        self.cursor.execute(query, (start_year, end_year))
        return self.cursor.fetchall()
    
    def get_movies_by_rating_range(self, min_rating, max_rating):
        """查询某个评分范围内的电影"""
        query = """
        SELECT * FROM Movie 
        WHERE imdb_rating BETWEEN %s AND %s
        ORDER BY imdb_rating DESC
        """
        self.cursor.execute(query, (min_rating, max_rating))
        return self.cursor.fetchall()
    
    def get_top_movies(self, n=10):
        """获取评分最高的N部电影"""
        query = "SELECT * FROM Movie ORDER BY imdb_rating DESC LIMIT %s"
        self.cursor.execute(query, (n,))
        return self.cursor.fetchall()
    
    def search_movies_by_keyword(self, keyword):
        """根据关键词搜索电影标题"""
        query = """
        SELECT * FROM Movie 
        WHERE title LIKE %s OR overview LIKE %s
        ORDER BY imdb_rating DESC
        """
        pattern = f"%{keyword}%"
        self.cursor.execute(query, (pattern, pattern))
        return self.cursor.fetchall()
    
    def get_movie_with_details(self, movie_id):
        """获取电影详情，包括导演、演员、类型"""
        # 基本信息
        movie = self.get_movie_by_id(movie_id)
        if not movie:
            return None
        
        # 导演
        query = """
        SELECT d.director_name 
        FROM Director d
        JOIN Movie m ON d.director_id = m.director_id
        WHERE m.movie_id = %s
        """
        self.cursor.execute(query, (movie_id,))
        movie['director'] = self.cursor.fetchone()['director_name']
        
        # 演员
        query = """
        SELECT a.actor_name 
        FROM Actor a
        JOIN Movie_Actor ma ON a.actor_id = ma.actor_id
        WHERE ma.movie_id = %s
        """
        self.cursor.execute(query, (movie_id,))
        movie['actors'] = [row['actor_name'] for row in self.cursor.fetchall()]
        
        # 类型
        query = """
        SELECT g.genre 
        FROM Genre g
        JOIN Movie_Genre mg ON g.genre_id = mg.genre_id
        WHERE mg.movie_id = %s
        """
        self.cursor.execute(query, (movie_id,))
        movie['genres'] = [row['genre'] for row in self.cursor.fetchall()]
        
        return movie

    # 2. 插入函数
    def add_movie(self, movie_data):
        """添加新电影
        movie_data: dict 包含以下字段:
            movie_id, director_id, title, year, certificate,
            runtime, imdb_rating, meta_score, votes, gross, overview, poster_link
        """
        query = """
        INSERT INTO Movie (movie_id, director_id, title, year,
                          certificate, runtime, imdb_rating, meta_score, votes,
                          gross, overview, poster_link)
        VALUES (%(movie_id)s, %(director_id)s, %(title)s, %(year)s,
                %(certificate)s, %(runtime)s, %(imdb_rating)s, %(meta_score)s,
                %(votes)s, %(gross)s, %(overview)s, %(poster_link)s)
        """
        self.cursor.execute(query, movie_data)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def add_movie_simple(self, movie_id, director_id, title, year,
                        certificate, runtime, imdb_rating, meta_score, votes,
                        gross, overview, poster_link):
        """简化版添加电影（参数形式）"""
        query = """
        INSERT INTO Movie (movie_id, director_id, title, year,
                          certificate, runtime, imdb_rating, meta_score, votes,
                          gross, overview, poster_link)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (movie_id, director_id, title, year,
                                    certificate, runtime, imdb_rating, meta_score,
                                    votes, gross, overview, poster_link))
        self.conn.commit()

    # 3. 更新函数
    def update_movie_rating(self, movie_id, new_rating):
        """更新电影评分"""
        query = "UPDATE Movie SET imdb_rating = %s WHERE movie_id = %s"
        self.cursor.execute(query, (new_rating, movie_id))
        self.conn.commit()
        return self.cursor.rowcount
    
    def update_movie(self, movie_id, update_data):
        """更新电影信息
        update_data: dict 要更新的字段和值
        """
        if not update_data:
            return 0
        
        set_clauses = [f"{key} = %s" for key in update_data.keys()]
        values = list(update_data.values()) + [movie_id]
        
        query = f"UPDATE Movie SET {', '.join(set_clauses)} WHERE movie_id = %s"
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.rowcount
    
    def update_movie_director(self, movie_id, new_director_id):
        """更新电影导演"""
        query = "UPDATE Movie SET director_id = %s WHERE movie_id = %s"
        self.cursor.execute(query, (new_director_id, movie_id))
        self.conn.commit()
        return self.cursor.rowcount

    # 4. 删除函数
    def delete_movie(self, movie_id):
        """删除电影及其关联记录"""
        try:
            # 先删除关联记录
            self.cursor.execute("DELETE FROM Movie_Actor WHERE movie_id = %s", (movie_id,))
            self.cursor.execute("DELETE FROM Movie_Genre WHERE movie_id = %s", (movie_id,))
            # 再删除电影
            self.cursor.execute("DELETE FROM Movie WHERE movie_id = %s", (movie_id,))
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            raise e

    # ==================== Director 表操作 ====================
    
    def get_all_directors(self):
        """获取所有导演"""
        query = "SELECT * FROM Director ORDER BY director_name"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_director_by_id(self, director_id):
        """根据ID获取导演"""
        query = "SELECT * FROM Director WHERE director_id = %s"
        self.cursor.execute(query, (director_id,))
        return self.cursor.fetchone()
    
    def get_director_by_name(self, director_name):
        """根据名称获取导演"""
        query = "SELECT * FROM Director WHERE director_name = %s"
        self.cursor.execute(query, (director_name,))
        return self.cursor.fetchone()
    
    def search_directors(self, keyword):
        """搜索导演"""
        query = "SELECT * FROM Director WHERE director_name LIKE %s ORDER BY director_name"
        self.cursor.execute(query, (f"%{keyword}%",))
        return self.cursor.fetchall()
    
    def add_director(self, director_name, director_id=None):
        """添加导演"""
        if director_id:
            query = "INSERT INTO Director (director_id, director_name) VALUES (%s, %s)"
            self.cursor.execute(query, (director_id, director_name))
        else:
            query = "INSERT INTO Director (director_name) VALUES (%s)"
            self.cursor.execute(query, (director_name,))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_director(self, director_id, new_name):
        """更新导演名称"""
        query = "UPDATE Director SET director_name = %s WHERE director_id = %s"
        self.cursor.execute(query, (new_name, director_id))
        self.conn.commit()
        return self.cursor.rowcount
    
    def delete_director(self, director_id):
        """删除导演（需确保没有关联电影）"""
        # 检查是否有电影关联
        query = "SELECT COUNT(*) as count FROM Movie WHERE director_id = %s"
        self.cursor.execute(query, (director_id,))
        result = self.cursor.fetchone()
        if result['count'] > 0:
            raise ValueError(f"Cannot delete director with {result['count']} associated movies")
        
        query = "DELETE FROM Director WHERE director_id = %s"
        self.cursor.execute(query, (director_id,))
        self.conn.commit()
        return self.cursor.rowcount
    
    def get_director_stats(self, director_id=None):
        """获取导演统计信息"""
        if director_id:
            query = """
            SELECT d.director_name, COUNT(m.movie_id) as movie_count,
                   AVG(m.imdb_rating) as avg_rating, MAX(m.imdb_rating) as max_rating
            FROM Director d
            LEFT JOIN Movie m ON d.director_id = m.director_id
            WHERE d.director_id = %s
            GROUP BY d.director_id
            """
            self.cursor.execute(query, (director_id,))
            return self.cursor.fetchone()
        else:
            query = """
            SELECT d.director_name, COUNT(m.movie_id) as movie_count,
                   AVG(m.imdb_rating) as avg_rating
            FROM Director d
            LEFT JOIN Movie m ON d.director_id = m.director_id
            GROUP BY d.director_id
            ORDER BY avg_rating DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()

    # ==================== Actor 表操作 ====================
    
    def get_all_actors(self):
        """获取所有演员"""
        query = "SELECT * FROM Actor ORDER BY actor_name"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_actor_by_id(self, actor_id):
        """根据ID获取演员"""
        query = "SELECT * FROM Actor WHERE actor_id = %s"
        self.cursor.execute(query, (actor_id,))
        return self.cursor.fetchone()
    
    def get_actor_by_name(self, actor_name):
        """根据名称获取演员"""
        query = "SELECT * FROM Actor WHERE actor_name = %s"
        self.cursor.execute(query, (actor_name,))
        return self.cursor.fetchone()
    
    def search_actors(self, keyword):
        """搜索演员"""
        query = "SELECT * FROM Actor WHERE actor_name LIKE %s ORDER BY actor_name"
        self.cursor.execute(query, (f"%{keyword}%",))
        return self.cursor.fetchall()
    
    def add_actor(self, actor_name, actor_id=None):
        """添加演员"""
        if actor_id:
            query = "INSERT INTO Actor (actor_id, actor_name) VALUES (%s, %s)"
            self.cursor.execute(query, (actor_id, actor_name))
        else:
            query = "INSERT INTO Actor (actor_name) VALUES (%s)"
            self.cursor.execute(query, (actor_name,))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_actor(self, actor_id, new_name):
        """更新演员名称"""
        query = "UPDATE Actor SET actor_name = %s WHERE actor_id = %s"
        self.cursor.execute(query, (new_name, actor_id))
        self.conn.commit()
        return self.cursor.rowcount
    
    def delete_actor(self, actor_id):
        """删除演员及其关联"""
        query = "DELETE FROM Movie_Actor WHERE actor_id = %s"
        self.cursor.execute(query, (actor_id,))
        query = "DELETE FROM Actor WHERE actor_id = %s"
        self.cursor.execute(query, (actor_id,))
        self.conn.commit()
        return self.cursor.rowcount
    
    def get_actor_stats(self, actor_id=None):
        """获取演员统计信息"""
        if actor_id:
            query = """
            SELECT a.actor_name, COUNT(m.movie_id) as movie_count,
                   AVG(m.imdb_rating) as avg_rating
            FROM Actor a
            LEFT JOIN Movie_Actor ma ON a.actor_id = ma.actor_id
            LEFT JOIN Movie m ON ma.movie_id = m.movie_id
            WHERE a.actor_id = %s
            GROUP BY a.actor_id
            """
            self.cursor.execute(query, (actor_id,))
            return self.cursor.fetchone()
        else:
            query = """
            SELECT a.actor_name, COUNT(m.movie_id) as movie_count,
                   AVG(m.imdb_rating) as avg_rating
            FROM Actor a
            LEFT JOIN Movie_Actor ma ON a.actor_id = ma.actor_id
            LEFT JOIN Movie m ON ma.movie_id = m.movie_id
            GROUP BY a.actor_id
            HAVING movie_count > 0
            ORDER BY movie_count DESC
            LIMIT 20
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()

    # ==================== Genre 表操作 ====================
    
    def get_all_genres(self):
        """获取所有类型"""
        query = "SELECT * FROM Genre ORDER BY genre"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_genre_by_id(self, genre_id):
        """根据ID获取类型"""
        query = "SELECT * FROM Genre WHERE genre_id = %s"
        self.cursor.execute(query, (genre_id,))
        return self.cursor.fetchone()
    
    def get_genre_by_name(self, genre_name):
        """根据名称获取类型"""
        query = "SELECT * FROM Genre WHERE genre = %s"
        self.cursor.execute(query, (genre_name,))
        return self.cursor.fetchone()
    
    def add_genre(self, genre, genre_id=None):
        """添加类型"""
        if genre_id:
            query = "INSERT INTO Genre (genre_id, genre) VALUES (%s, %s)"
            self.cursor.execute(query, (genre_id, genre))
        else:
            query = "INSERT INTO Genre (genre) VALUES (%s)"
            self.cursor.execute(query, (genre,))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_genre(self, genre_id, new_genre):
        """更新类型名称"""
        query = "UPDATE Genre SET genre = %s WHERE genre_id = %s"
        self.cursor.execute(query, (new_genre, genre_id))
        self.conn.commit()
        return self.cursor.rowcount
    
    def delete_genre(self, genre_id):
        """删除类型及其关联"""
        query = "DELETE FROM Movie_Genre WHERE genre_id = %s"
        self.cursor.execute(query, (genre_id,))
        query = "DELETE FROM Genre WHERE genre_id = %s"
        self.cursor.execute(query, (genre_id,))
        self.conn.commit()
        return self.cursor.rowcount
    
    def get_genre_stats(self):
        """获取各类型电影统计"""
        query = """
        SELECT g.genre_id, g.genre, COUNT(m.movie_id) as movie_count,
               AVG(m.imdb_rating) as avg_rating
        FROM Genre g
        LEFT JOIN Movie_Genre mg ON g.genre_id = mg.genre_id
        LEFT JOIN Movie m ON mg.movie_id = m.movie_id
        GROUP BY g.genre_id, g.genre
        ORDER BY movie_count DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # ==================== Movie_Actor 关联表操作 ====================
    
    def add_movie_actor(self, movie_id, actor_id):
        """为电影添加演员"""
        query = "INSERT INTO Movie_Actor (movie_id, actor_id) VALUES (%s, %s)"
        self.cursor.execute(query, (movie_id, actor_id))
        self.conn.commit()
        return self.cursor.rowcount
    
    def remove_movie_actor(self, movie_id, actor_id=None):
        """从电影中移除演员，如果actor_id为None则移除所有演员"""
        if actor_id:
            query = "DELETE FROM Movie_Actor WHERE movie_id = %s AND actor_id = %s"
            self.cursor.execute(query, (movie_id, actor_id))
        else:
            query = "DELETE FROM Movie_Actor WHERE movie_id = %s"
            self.cursor.execute(query, (movie_id,))
        self.conn.commit()
        return self.cursor.rowcount
    
    def get_movie_actors(self, movie_id):
        """获取电影的所有演员"""
        query = """
        SELECT a.* FROM Actor a
        JOIN Movie_Actor ma ON a.actor_id = ma.actor_id
        WHERE ma.movie_id = %s
        ORDER BY a.actor_name
        """
        self.cursor.execute(query, (movie_id,))
        return self.cursor.fetchall()
    
    def get_actor_movies(self, actor_id):
        """获取演员参演的所有电影"""
        query = """
        SELECT m.* FROM Movie m
        JOIN Movie_Actor ma ON m.movie_id = ma.movie_id
        WHERE ma.actor_id = %s
        ORDER BY m.imdb_rating DESC
        """
        self.cursor.execute(query, (actor_id,))
        return self.cursor.fetchall()

    # ==================== Movie_Genre 关联表操作 ====================
    
    def add_movie_genre(self, movie_id, genre_id):
        """为电影添加类型"""
        query = "INSERT INTO Movie_Genre (movie_id, genre_id) VALUES (%s, %s)"
        self.cursor.execute(query, (movie_id, genre_id))
        self.conn.commit()
        return self.cursor.rowcount
    
    def remove_movie_genre(self, movie_id, genre_id=None):
        """从电影中移除类型，如果genre_id为None则移除所有类型"""
        if genre_id:
            query = "DELETE FROM Movie_Genre WHERE movie_id = %s AND genre_id = %s"
            self.cursor.execute(query, (movie_id, genre_id))
        else:
            query = "DELETE FROM Movie_Genre WHERE movie_id = %s"
            self.cursor.execute(query, (movie_id,))
        self.conn.commit()
        return self.cursor.rowcount
    
    def get_movie_genres(self, movie_id):
        """获取电影的所有类型"""
        query = """
        SELECT g.* FROM Genre g
        JOIN Movie_Genre mg ON g.genre_id = mg.genre_id
        WHERE mg.movie_id = %s
        ORDER BY g.genre
        """
        self.cursor.execute(query, (movie_id,))
        return self.cursor.fetchall()

    # ==================== 复杂查询 ====================
    
    def get_movies_with_filters(self, year=None, genre=None, min_rating=None, 
                                 director=None, actor=None, limit=50):
        """多条件筛选电影"""
        conditions = []
        params = []
        
        base_query = """
        SELECT DISTINCT m.*, d.director_name 
        FROM Movie m
        JOIN Director d ON m.director_id = d.director_id
        """
        
        if genre:
            base_query += " JOIN Movie_Genre mg ON m.movie_id = mg.movie_id JOIN Genre g ON mg.genre_id = g.genre_id"
            conditions.append("g.genre = %s")
            params.append(genre)
        
        if actor:
            base_query += " JOIN Movie_Actor ma ON m.movie_id = ma.movie_id JOIN Actor a ON ma.actor_id = a.actor_id"
            conditions.append("a.actor_name = %s")
            params.append(actor)
        
        if year:
            conditions.append("m.year = %s")
            params.append(year)
        
        if min_rating:
            conditions.append("m.imdb_rating >= %s")
            params.append(min_rating)
        
        if director:
            conditions.append("d.director_name = %s")
            params.append(director)
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY m.imdb_rating DESC LIMIT %s"
        params.append(limit)
        
        self.cursor.execute(base_query, tuple(params))
        return self.cursor.fetchall()
    
    def get_yearly_stats(self):
        """获取每年电影统计"""
        query = """
        SELECT year, COUNT(*) as movie_count,
               AVG(imdb_rating) as avg_rating, MAX(imdb_rating) as max_rating
        FROM Movie
        GROUP BY year
        ORDER BY year DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_top_grossing_movies(self, n=10):
        """获取票房最高的电影"""
        query = """
        SELECT * FROM Movie 
        WHERE gross IS NOT NULL
        ORDER BY gross DESC 
        LIMIT %s
        """
        self.cursor.execute(query, (n,))
        return self.cursor.fetchall()
    
    def get_frequent_collaborations(self, min_movies=2):
        """获取频繁合作的导演-演员组合"""
        query = """
        SELECT d.director_name, a.actor_name, COUNT(*) as movie_count
        FROM Movie m
        JOIN Director d ON m.director_id = d.director_id
        JOIN Movie_Actor ma ON m.movie_id = ma.movie_id
        JOIN Actor a ON ma.actor_id = a.actor_id
        GROUP BY d.director_id, a.actor_id
        HAVING movie_count >= %s
        ORDER BY movie_count DESC
        """
        self.cursor.execute(query, (min_movies,))
        return self.cursor.fetchall()


# ==================== 使用示例 ====================

if __name__ == '__main__':
    db = MovieDatabase()
    
    # 示例1: 查询导演的所有电影
    print("=== Christopher Nolan的电影 ===")
    movies = db.get_movies_by_director("Christopher Nolan")
    for movie in movies[:3]:
        print(f"  {movie['title']}: {movie['imdb_rating']}")
    
    # 示例2: 获取评分最高的10部电影
    print("\n=== 评分最高的10部电影 ===")
    top_movies = db.get_top_movies(10)
    for movie in top_movies[:3]:
        print(f"  {movie['title']}: {movie['imdb_rating']}")
    
    # 示例3: 搜索电影
    print("\n=== 搜索关键词 'Batman' ===")
    results = db.search_movies_by_keyword("Batman")
    for movie in results[:3]:
        print(f"  {movie['title']}")
    
    # 示例4: 多条件筛选
    print("\n=== 筛选: 2010年后、评分>8.0的电影 ===")
    filtered = db.get_movies_with_filters(min_rating=8.0, limit=5)
    for movie in filtered:
        print(f"  {movie['title']} ({movie['year']}): {movie['imdb_rating']}")
    
    # 示例5: 获取类型统计
    print("\n=== 各类型电影统计 ===")
    stats = db.get_genre_stats()
    for stat in stats[:5]:
        print(f"  {stat['genre']}: {stat['movie_count']}部")
    
    # 示例6: 获取电影详情
    print("\n=== 获取电影详情 (movie_id=1) ===")
    detail = db.get_movie_with_details(1)
    if detail:
        print(f"  标题: {detail['title']}")
        print(f"  导演: {detail['director']}")
        print(f"  演员: {', '.join(detail['actors'][:3])}...")
        print(f"  类型: {', '.join(detail['genres'])}")
    
    db.close()
    print("\n所有操作完成！")
