# MongoDB-AirBnB-analysis

## Data Prepareation
## Analysis

### Q1: AirBnB Search: Display list of stays in Salem with details: name, neighbourhood, room type, how many guests it accommodates, property type and amenities, per night’s cost and is available for the next two days in descending order of rating. 

```
[
  {
    $lookup: {
      from: "Salem_calendar_unembedded",
      localField: "id",
      foreignField: "listing_id",
      as: "availability",
    },
  },
  {
    $unwind: "$availability",
  },
  {
    $match: {
      "availability.available": "t",
      $expr: {
        $or: [
          {
            $eq: [
              {
                $toDate: {
                  $dateFromParts: {
                    year: {
                      $year: {
                        $add: [
                          new Date(),
                          86400000,
                        ],
                      },
                    },
                    month: {
                      $month: {
                        $add: [
                          new Date(),
                          86400000,
                        ],
                      },
                    },
                    day: {
                      $dayOfMonth: {
                        $add: [
                          new Date(),
                          86400000,
                        ],
                      },
                    },
                  },
                },
              },
              // Tomorrow
              {
                $toDate: "$availability.date",
              },
            ],
          },
          {
            $eq: [
              {
                $toDate: {
                  $dateFromParts: {
                    year: {
                      $year: {
                        $add: [
                          new Date(),
                          172800000,
                        ],
                      },
                    },
                    month: {
                      $month: {
                        $add: [
                          new Date(),
                          172800000,
                        ],
                      },
                    },
                    day: {
                      $dayOfMonth: {
                        $add: [
                          new Date(),
                          172800000,
                        ],
                      },
                    },
                  },
                },
              },
              // Day after tomorrow
              {
                $toDate: "$availability.date",
              },
            ],
          },
        ],
      },
    },
  },
  {
    $group: {
      _id: "$_id",
      name: {
        $first: "$name",
      },
      neighbourhood: {
        $first: "$neighbourhood_cleansed",
      },
      room_type: {
        $first: "$room_type",
      },
      accommodates: {
        $first: "$accommodates",
      },
      property_type: {
        $first: "$property_type",
      },
      amenities: {
        $first: "$amenities",
      },
      price: {
        $first: "$price",
      },
      availability: {
        $push: "$availability",
      },
    },
  },
  {
    $sort: {
      review_scores_rating: -1,
    },
  },
]
```

### Q2

### Q3

### Q4

### Q5

### Q6
