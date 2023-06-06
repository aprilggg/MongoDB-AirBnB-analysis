# MongoDB AirBnB Analysis

## Data Preparation
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

### Q2: Are there any neighbourhoods in any of the cities that don’t have any listings?
```
[
  {
    $lookup: {
      from: "Portland_listing",
      localField: "neighbourhood",
      foreignField: "neighbourhood_cleansed",
      as: "listing",
    },
  },
  {
    $match: {
      listing: {
        $eq: [],
      },
    },
  },
]
```


### Q3: (Availability for booking) For “Entire home/apt” type listings in Salem provide its availability estimate for each month – which chunks of time are bookable? Display listing’s name, whether it’s Entire home/apt, month, availability “from – to” date/or just date if minimum nights is 1, and minimum nights. 

### NOTE: availability estimate: Chunks of time within which booking is possible. Compare the number of minimum nights against the consecutively available days. If there is availability on Friday, but Thursday, Saturday and Sunday are not available and the minimum number of days is 2, then Friday also doesn’t qualify for booking and is not part of the final result. Also, note, the minimum nights bookable for a listing may vary based on the day of the week). 
```
[
  {
    $match:
      /**
       * query: The query in MQL.
       */
      {
        room_type: "Entire home/apt",
      },
  },
  {
    $lookup:
      /**
       * from: The target collection.
       * localField: The local join field.
       * foreignField: The target join field.
       * as: The name for the results.
       * pipeline: Optional pipeline to run on the foreign collection.
       * let: Optional variables to use in the pipeline field stages.
       */
      {
        from: "Salem_calendar_unembedded",
        localField: "id",
        foreignField: "listing_id",
        as: "calendar_info",
      },
  },
  {
    $unwind: "$calendar_info",
  },
  {
    $addFields:
      /**
       * newField: The new field name.
       * expression: The new field expression.
       */
      {
        month: {
          $month: {
            $dateFromString: {
              dateString: "$calendar_info.date",
            },
          },
        },
        year: {
          $year: {
            $dateFromString: {
              dateString: "$calendar_info.date",
            },
          },
        },
        day: {
          $dayOfMonth: {
            $dateFromString: {
              dateString: "$calendar_info.date",
            },
          },
        },
        date: {
          $dateFromString: {
            dateString: "$calendar_info.date",
          },
        },
        available: "$calendar_info.available",
        min_night:
          "$calendar_info.minimum_nights",
      },
  },
  {
    $project:
      /**
       * specifications: The fields to
       *   include or exclude.
       */
      {
        name: 1,
        date: 1,
        available: 1,
        min_night: 1,
        day: 1,
        month: 1,
        year: 1,
      },
  },
  {
    $match:
      /**
       * query: The query in MQL.
       */
      {
        available: "t",
      },
  },
  {
    $group:
      /**
       * _id: The id of the group.
       * fieldN: The first field name.
       */
      {
        _id: {
          name: "$name",
          year: "$year",
          month: "$month",
          min_night: "$min_night",
        },
        items: {
          $addToSet: {
            date: "$day",
          },
        },
      },
  },
]
```
### Q4: Booking Trend for Spring versus Winter: For “Entire home/apt” type listings in Portland provide it’s availability estimate for each month of Spring and Winter this year.

```
[
  {
    $addFields: {
      month: {
        $month: {
          $dateFromString: {
            dateString: "$date",
          },
        },
      },
      day: {
        $dayOfMonth: {
          $dateFromString: {
            dateString: "$date",
          },
        },
      },
      year: {
        $year: {
          $dateFromString: {
            dateString: "$date",
          },
        },
      },
    },
  },
  {
    $addFields: {
      season: {
        $switch: {
          branches: [
            {
              case: {
                $in: ["$month", [12, 1, 2]],
              },
              then: "Winter",
            },
            {
              case: {
                $in: ["$month", [3, 4, 5]],
              },
              then: "Spring",
            },
            {
              case: {
                $in: ["$month", [6, 7, 8]],
              },
              then: "Summer",
            },
            {
              case: {
                $in: ["$month", [9, 10, 11]],
              },
              then: "Fall",
            },
          ],
          default: "Unknown",
        },
      },
    },
  },
  {
    $match: {
      $and: [
        {
          year: 2023,
        },
        {
          $or: [
            {
              $and: [
                {
                  season: "Spring",
                },
                {
                  available: "t",
                },
              ],
            },
            {
              $and: [
                {
                  season: "Winter",
                },
                {
                  available: "t",
                },
              ],
            },
          ],
        },
      ],
    },
  },
  {
    $lookup: {
      from: "Portland_listing",
      localField: "listing_id",
      foreignField: "id",
      as: "listing",
    },
  },
  {
    $match: {
      "listing.room_type": "Entire home/apt",
    },
  },
  {
    $project: {
      listing_id: "$listing_id",
      month: "$month",
      season: "$season",
    },
  },
  {
    $group: {
      _id: {
        listing_id: "$listing_id",
        month: "$month",
        season: "$season",
      },
      count: {
        $sum: 1,
      },
    },
  },
  {
    $sort: {
      "_id.listing_id": 1,
      "_id.month": 1,
    },
  },
]
```
### Q5 (Booking trend) For each city, how many reviews are received for December of each year?
```
[
  {
    $addFields: {
      month: {
        $month: "$date",
      },
      year: {
        $year: "$date",
      },
    },
  },
  {
    $match: {
      month: 12,
    },
  },
  {
    $group: {
      _id: "$year",
      count: {
        $sum: 1,
      },
    },
  },
  {
    $sort: {
      _id: 1,
    },
  },
]
```
### Q6: Reminder to Book Again: In Salem, there any listings that a reviewer has reviewed more than thrice that is also available in the same month as was reviewed by them previously? (check against all the months that the previous reviews were posted on, if any match then it qualifies). AND are there any other listings by the same host that can be suggested? Display listing’s name, url, description, host’s name, reviewer name, whether previously booked (more than thrice and is available in the same month as was reviewed by them previously), availability days, minimum and maximum nights booking allowed.
```
[
  {
    $addFields: {
      month: {
        $month: {
          $dateFromString: {
            dateString: "$date",
          },
        },
      },
    },
  },
  {
    $group: {
      _id: {
        listing_id: "$listing_id",
        reviewer_id: "$reviewer_id",
      },
      count: {
        $sum: 1,
      },
    },
  },
  {
    $match: {
      count: {
        $gt: 3,
      },
    },
  },
  {
    $lookup: {
      from: "Salem_reviews_unembedded",
      localField: "_id.listing_id",
      foreignField: "listing_id",
      as: "match",
    },
  },
  {
    $project: {
      match: {
        $filter: {
          input: "$match",
          as: "m",
          cond: {
            $eq: [
              "$$m.reviewer_id",
              "$_id.reviewer_id",
            ],
          },
        },
      },
    },
  },
  {
    $project: {
      listing_id: 1,
      reviewer_id: 1,
      date: "$match.date",
    },
  },
  {
    $unwind: "$date",
  },
  {
    $project: {
      listing_id: 1,
      reviewer_id: 1,
      month: {
        $month: {
          $dateFromString: {
            dateString: "$date",
          },
        },
      },
    },
  },
  {
    $lookup: {
      from: "Salem_calendar_unembedded",
      localField: "_id.listing_id",
      foreignField: "listing_id",
      as: "calendar",
    },
  },
  {
    $project: {
      calendar: {
        $filter: {
          input: "$calendar",
          as: "c",
          cond: {
            $eq: ["$$c.available", "t"],
          },
        },
      },
      month: 1,
    },
  },
  {
    $project: {
      listing_id: 1,
      reviewer_id: 1,
      month: 1,
      datecal: "$calendar.date",
    },
  },
  {
    $unwind: "$datecal",
  },
  {
    $project: {
      listing_id: 1,
      reviewer_id: 1,
      month: 1,
      monthcal: {
        $month: {
          $dateFromString: {
            dateString: "$datecal",
          },
        },
      },
    },
  },
  {
    $match: {
      $expr: {
        $eq: ["$month", "$monthcal"],
      },
    },
  },
  {
    $group: {
      _id: {
        listing_id: "$_id.listing_id",
        reviewer_id: "$_id.reviewer_id",
      },
      count: {
        $sum: 1,
      },
    },
  },
  {
    $project: {
      listing_id: 1,
      reviewer_id: 1,
    },
  },
  {
    $lookup: {
      from: "Salem_listing",
      localField: "_id.listing_id",
      foreignField: "id",
      as: "listing",
    },
  },
  {
    $project: {
      listing_id: 1,
      reviewer_id: 1,
      host_id: "$listing.host_id",
    },
  },
  {
    $unwind: "$host_id",
  },
  {
    $lookup: {
      from: "Salem_listing",
      localField: "host_id",
      foreignField: "host_id",
      as: "hostlist",
    },
  },
  {
    $project: {
      listing_id: 1,
      reviewer_id: 1,
      host_id: "$hostlist.host_id",
      host_listing: "$hostlist.id",
    },
  },
  {
    $unwind: "$host_id",
  },
  {
    $unwind: "$host_listing",
  },
  {
    $group: {
      _id: {
        listing_id: "$_id.listing_id",
        reviewer_id: "$_id.reviewer_id",
        host_id: "$host_id",
        host_listing: "$host_listing",
      },
      count: {
        $sum: 1,
      },
    },
  },
  {
    $addFields: {
      previously_booked_3_month: {
        $cond: {
          if: {
            $eq: [
              "$_id.host_listing",
              "$_id.listing_id",
            ],
          },
          then: "yes",
          else: "no",
        },
      },
    },
  },
  {
    $lookup: {
      from: "Salem_listing",
      localField: "_id.listing_id",
      foreignField: "id",
      as: "listingdetails",
    },
  },
  {
    $project: {
      listing_id: 1,
      reviewer_id: 1,
      host_id: 1,
      host_listing: 1,
      previously_booked_3_month: 1,
      listing_name: "$listingdetails.name",
      listing_url: "$listingdetails.listing_url",
      description: "$listingdetails.description",
      host_name: "$listingdetails.host_name",
      availability_365:
        "$listingdetails.availability_365",
      minimum_nights:
        "$listingdetails.minimum_nights",
      maximum_nights:
        "$listingdetails.maximum_nights",
    },
  },
  {
    $unwind: "$listing_name",
  },
  {
    $unwind: "$listing_url",
  },
  {
    $unwind: "$description",
  },
  {
    $unwind: "$host_name",
  },
  {
    $unwind: "$availability_365",
  },
  {
    $unwind: "$minimum_nights",
  },
  {
    $unwind: "$maximum_nights",
  },
  {
    $lookup: {
      from: "Salem_reviews_unembedded",
      localField: "_id.reviewer_id",
      foreignField: "reviewer_id",
      as: "reviewer_details",
    },
  },
  {
    $project: {
      listing_id: 1,
      reviewer_id: 1,
      host_id: 1,
      host_listing: 1,
      previously_booked_3_month: 1,
      listing_name: 1,
      listing_url: 1,
      description: 1,
      host_name: 1,
      availability_365: 1,
      minimum_nights: 1,
      maximum_nights: 1,
      reviewer_name:
        "$reviewer_details.reviewer_name",
    },
  },
  {
    $unwind: "$reviewer_name",
  },
  {
    $group: {
      _id: {
        listing_id: "$_id.host_listing",
        reviewer_id: "$_id.reviewer_id",
        host_id: "$_id.host_id",
        previously_booked_3_month:
          "$previously_booked_3_month",
        listing_name: "$listing_name",
        listing_url: "$listing_url",
        description: "$description",
        host_name: "$host_name",
        availability_365: "$availability_365",
        minimum_nights: "$minimum_nights",
        maximum_nights: "$maximum_nights",
        reviewer_name: "$reviewer_name",
      },
    },
  },
]
```
