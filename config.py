import os

env_vars = {
  # Get From my.telegram.org
  "API_HASH": "057fd0be9d7c38526b143c582bceb24b",
  # Get From my.telegram.org
  "API_ID": "20445873",
  #Get For @BotFather
  "BOT_TOKEN": "7716045686:AAEF1du2uLWudLXUH-z-uVpTF5QqmEjIINA",
  # Get For tembo.io
  "DATABASE_URL_PRIMARY": "postgresql://postgres:4NQDGksWwMhyfcP5@delicately-purposeful-hen.data-1.apse1.tembo.io:5432/postgres",
  # Logs Channel Username Without @
  "CACHE_CHANNEL": "Dump2075",
  # Force Subs Channel username without @
  "CHANNEL": "Manga_Campus",
  # {chap_num}: Chapter Number
  # {chap_name} : Manga Name
  # Ex : Chapter {chap_num} {chap_name} @Manhwa_Arena
  "F1": "[MC] [{chap_num}] {chap_name} @Manga_Campus",
  "F2": "[{chap_num}] [MW] {chap_name} [@Manhwa_Weebs]",
# Thumb 
  "TH1": "TH1.jpg",
  "TH2": "TH2.jpg",
  #Banner
  "B1": ["first.jpg", "last.jpg"],
  "B2": ["TH2.jpg", "thumb.jpg"]
}
#OWNER_ID = int(os.environ.get("OWNER_ID", "1788144071")) # Retrieve the AUTH_USERS environment variable as a space-separated string and convert to a list of integers 
#auth_users = [int(user_id) for user_id in os.environ.get('5164955785,7716045686,6975428639,1302933634').split()] # Append OWNER_ID to the list of auth_users 
#AUTH_USERS = auth_users + [OWNER_ID]
dbname = env_vars.get('DATABASE_URL_PRIMARY') or env_vars.get('DATABASE_URL') or 'sqlite:///test.db'

if dbname.startswith('postgres://'):
    dbname = dbname.replace('postgres://', 'postgresql://', 1)
    
