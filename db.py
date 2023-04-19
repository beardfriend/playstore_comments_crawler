import pymysql


def connect():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        passwd="",
    )

    try:
        cursor = conn.cursor()
        cursor.execute(createDatabaseQuery)
        cursor.execute(useDatabaseQuery)
        cursor.execute(createTableQueryReviews)
        cursor.execute(createTableQueryApps)
        conn.commit()
        cursor.close()

    except:
        conn.close()

    return conn


createDatabaseQuery = """
CREATE DATABASE IF NOT EXISTS playstore"""

useDatabaseQuery = """
USE playstore"""

createTableQueryReviews = """
CREATE TABLE IF NOT EXISTS reviews
(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    app_id INT NOT NULL,
    user_name VARCHAR(255),
    rating FLOAT(8, 1),
    reviewed_at DATE,
    content TEXT,
    useful_count INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)"""

createTableQueryApps = """
CREATE TABLE IF NOT EXISTS apps
(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    request_count INT,
    url VARCHAR(100),
    name VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)"""

insertQueryApps = """
    INSERT INTO apps (name, request_count, url) VALUES (%s, %s, %s)"""

insertQueryreviews = """
    INSERT INTO reviews (app_id, user_name, rating, reviewed_at, content, useful_count)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
