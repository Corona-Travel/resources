db = db.getSiblingDB("corona_travel")

// db.place.createIndex({ place_id: 1 }, { unique: true })
db.places.insert({ name: "Moscow", place_id: "moscow", pos: [55.749792, 37.632495] })
db.places.insert({ name: "Madrid", place_id: "madrid", pos: [40.416775, -3.703790] })
db.places.insert({ name: "New York", place_id: "ny", pos: [40.730610, -73.935242] })

db.facts.insert({ name: "Req Square", description: "Red Square was built in 16-th century", fact_id: "moscow_red_sqr", pos: [55.749792, 37.632495] })
db.facts.insert({ name: "Manhattan", description: "Manhattan is historical center on NY", fact_id: "ny_manh", pos: [40.730610, -73.935242] })
