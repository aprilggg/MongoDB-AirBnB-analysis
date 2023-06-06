from pymongo import MongoClient

# Connection details
connection_string = "<connection_string>"
database_name = "<database_name>"
collection_name = "<collection_name>"

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

