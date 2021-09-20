# from dotenv import load_dotenv
import os

import pandas as pd
import pymongo

# Set environment variables
os.environ['MONGO_DB_ADMIN_USER'] = 'Admin'
os.environ['MONGO_DB_ADMIN_PASSWORD'] = 'Good21luck!'

DATABASE = "PSCR_First"
COLLECTION = "Collection_2"
# load_dotenv() # use dotenv to hide sensitive credential as environment variables
DATABASE_URL = f'mongodb+srv://{os.environ.get("MONGO_DB_ADMIN_USER")}:{os.environ.get("MONGO_DB_ADMIN_PASSWORD")}' \
               '@cluster0.ytpyp.mongodb.net/{}?' \
               'retryWrites=true&w=majority'.format(DATABASE)  # get connection url from environment


class DataBase:
    def __init__(self):
        self.mongo_db = None
        self.client = None

    def connect(self):
        print("Connecting ...")
        self.client = pymongo.MongoClient(DATABASE_URL)  # establish connection with database
        # database

        db = self.client[DATABASE]
        # collection
        collection = db[COLLECTION]
        return collection

    def setDataBase(self, databse=DATABASE, collection=COLLECTION):
        db = self.client[databse]
        collection = db[collection]
        print("Connected")

        return collection

    def addDF(self, collection, df):
        df.reset_index(inplace=True)
        data_dict = df.to_dict("records")
        print(type(collection))
        # Insert collection
        collection.insert_many(data_dict)

    def read_mongo(self, collection, query={}):
        # Make a query to the specific DB and Collection
        cursor = collection.find(query)

        # Expand the cursor and construct the DataFrame
        df = pd.DataFrame(list(cursor))
        return df
