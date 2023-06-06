from pymongo import MongoClient

# Connection details
connection_string = "mongodb://514investigation:2UgCpgjiOIMKn8Hq2QET4Oj07nUJWP68nzpij9QtQ2ul1HC0oxUSFFKOiEPnzFVql2zyTRcJYi2bACDbkZHVEA==@514investigation.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@514investigation@"
database_name = "airbnb"
collection_name = "Salem_reviews_unembedded"

client = MongoClient(connection_string)
db = client[database_name]
collection = db[collection_name]

doc = collection.aggregate([   
    { '$addFields': {'nmonth': {'$month': {'$dateFromString': {'dateString': "$date"}}},  
                     'nyear': {'$year': {'$dateFromString': {'dateString': "$date"}}}}}, 
    { '$match': {'nmonth': 12}}, 
    { '$group': {'_id': '$nyear', 'count': {'$sum': 1}}}, 
    { '$sort': { '_id': 1} }
])

print(list(doc))

