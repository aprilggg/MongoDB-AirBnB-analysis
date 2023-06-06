from pymongo import MongoClient
import copy

# Connection details
connection_string = "<connection_string>"
database_name = "<database_name>"
collection_name = "<collection_name>"

client = MongoClient(connection_string)
db = client[database_name]
collection = db[collection_name]

pipeline = [
    {
        '$match': {
            'room_type': 'Entire home/apt'
        }
    }, {
        '$lookup': {
            'from': 'Salem_calendar_unembedded', 
            'localField': 'id', 
            'foreignField': 'listing_id', 
            'as': 'calendar_info'
        }
    }, {
        '$unwind': '$calendar_info'
    }, {
        '$addFields': {
            'month': {
                '$month': {
                    '$dateFromString': {
                        'dateString': '$calendar_info.date'
                    }
                }
            }, 
            'year': {
                '$year': {
                    '$dateFromString': {
                        'dateString': '$calendar_info.date'
                    }
                }
            }, 
            'day': {
                '$dayOfMonth': {
                    '$dateFromString': {
                        'dateString': '$calendar_info.date'
                    }
                }
            }, 
            'date': {
                '$dateFromString': {
                    'dateString': '$calendar_info.date'
                }
            }, 
            'available': '$calendar_info.available', 
            'min_night': '$calendar_info.minimum_nights'
        }
    }, {
        '$project': {
            'name': 1, 
            'date': 1, 
            'available': 1, 
            'min_night': 1, 
            'day': 1, 
            'month': 1, 
            'year': 1
        }
    }, {
        '$match': {
            'available': 't'
        }
    }, {
        '$group': {
            '_id': {
                'name': '$name', 
                'year': '$year', 
                'month': '$month', 
                'min_night': '$min_night'
            }, 
            'items': {
                '$addToSet': {
                    'date': '$day'
                }
            }
        }
    }
]

doc = list(collection.aggregate(pipeline))
final = []
for lst in doc:
    temp = []
    for day in lst['items']:
        temp.append(day['date'])
    final.append([lst['_id'], temp])

def check_availability(min_night, days):
    rs = []
    if len(days) < min_night:
        return rs
    if min_night == 1:
        for i in days:
            rs.append([i,i])
        return rs
    cnt = 1
    curr = days[0]
    start = days[0]
    for i in range(1, len(days)):
        if days[i] == curr+1:
            cnt += 1
        else:
            if cnt >= min_night:
                rs.append([start, curr])
            start = days[i]
            cnt = 0
        curr = days[i]
    if cnt >= min_night:
        rs.append([start, curr])
    return rs
for j in range(100):
    lst = check_availability(final[j][0]['min_night'], final[j][1])
    if len(lst)==0:
        print(final[j][0]['name'] + ' has no availabily in ' + str(final[j][0]['year']) + '/' + str(final[j][0]['month']))
    else:
        print(final[j][0]['name'] + ' has availabily in ' + str(final[j][0]['year']) + '/' + str(final[j][0]['month']) + ' from ')
        for l in lst:
            print(str(l[0]) + ' to ' + str(l[1]))
    
    


