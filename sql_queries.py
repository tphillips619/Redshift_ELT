import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events (
    artist VARCHAR,
    auth VARCHAR,
    firstName VARCHAR,
    gender VARCHAR,
    itemInSession INT,
    lastName VARCHAR,
    length DOUBLE PRECISION,
    level VARCHAR,
    location VARCHAR,
    method VARCHAR,
    page VARCHAR,
    registration BIGINT,
    sessionId INT,
    song VARCHAR,
    status INT,
    ts TIMESTAMP,
    userAgent VARCHAR,
    userId INT
)
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs (
    num_songs INT,
    artist_id VARCHAR,
    artist_latitude DOUBLE PRECISION,
    artist_location VARCHAR,
    artist_logitude DOUBLE PRECISION,
    artist_name VARCHAR,
    song_id VARCHAR,
    title VARCHAR,
    duration DOUBLE PRECISION,
    year INT
)
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays (
  songplay_id INT IDENTITY(0,1) PRIMARY KEY, 
  start_time TIMESTAMP, 
  user_id INT NOT NULL, 
  level VARCHAR, 
  song_id VARCHAR, 
  artist_id VARCHAR, 
  session_id INT, 
  location VARCHAR, 
  user_agent VARCHAR
)
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users (
  user_id int PRIMARY KEY,
  first_name VARCHAR, 
  last_name VARCHAR,
  gender VARCHAR, 
  level VARCHAR
)
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs (
  song_id VARCHAR PRIMARY KEY, 
  title VARCHAR, 
  artist_id VARCHAR, 
  year INT, 
  duration NUMERIC
)
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists (
  artist_id VARCHAR PRIMARY KEY, 
  name VARCHAR, 
  location VARCHAR,
  latitude DOUBLE PRECISION, 
  longitude DOUBLE PRECISION
  )
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time (
  time_id INT IDENTITY(0,1) PRIMARY KEY,
  start_time TIMESTAMP NOT NULL, 
  hour INT, 
  day INT,
  week INT, 
  month INT, 
  year INT, 
  weekday INT)
""")

# STAGING TABLES

staging_events_copy = ("""
COPY staging_events FROM '{}'
IAM_ROLE '{}'
JSON '{}'
REGION 'us-west-2'
TIMEFORMAT 'epochmillisecs'
""").format(config['S3']['LOG_DATA'], 
            config['IAM_ROLE']['ARN'], 
            config['S3']['LOG_JSONPATH'])

staging_songs_copy = ("""
COPY staging_songs FROM '{}'
IAM_ROLE '{}'
JSON 'auto'
REGION 'us-west-2'
""").format(config['S3']['SONG_DATA'], 
            config['IAM_ROLE']['ARN'])

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays (
    start_time,
    user_id,
    level,
    song_id,
    artist_id,
    session_id,
    location,
    user_agent
) SELECT
    se.ts, se.userid, se.level, ss.song_id, ss.artist_id, se.sessionid, se.location, se.useragent 
FROM
    staging_events se 
JOIN
    staging_songs ss ON se.artist = ss.artist_name;
""")

user_table_insert = ("""
INSERT INTO users (
    user_id,
    first_name,
    last_name,
    gender,
    level
)SELECT
    DISTINCT(userId
    ), firstName, lastName, gender, level
FROM
    staging_events
WHERE
    userId IS NOT NULL
""")

song_table_insert = ("""
INSERT INTO songs (
    song_id,
    title,
    artist_id,
    year,
    duration
)SELECT
    song_id, title, artist_id, year, duration
FROM
    staging_songs
""")

artist_table_insert = ("""
INSERT INTO artists (
    artist_id,
    name,
    location,
    latitude,
    longitude
)SELECT
    artist_id,
    artist_name,
    artist_location,
    artist_latitude,
    artist_logitude
FROM
    staging_songs
""")

time_table_insert = ("""
INSERT INTO time (
    start_time,
    hour,
    day,
    week,
    month,
    year,
    weekday
)SELECT start_time,
    EXTRACT(hour FROM start_time) AS hour,
    EXTRACT(day FROM start_time) AS day,
    EXTRACT(week FROM start_time) AS week,
    EXTRACT(month FROM start_time) AS month,
    EXTRACT(year FROM start_time) AS year,
    EXTRACT(weekday FROM start_time) as weekday
FROM songplays
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create,
                        user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop,
                      song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert,
                        time_table_insert]
