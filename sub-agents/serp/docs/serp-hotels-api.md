
Google Hotels API
API uptime
99.996%
Our Google Hotels API allows you to scrape hotel and vacation rental results from Google Hotels. The API is accessed through the following endpoint: /search?engine=google_hotels.

A user may query the following: https://serpapi.com/search?engine=google_hotels utilizing a GET request. Head to the playground for a live and interactive demo.

API Parameters
Search Query
q

Required

Parameter defines the search query. You can use anything that you would use in a regular Google Hotels search.

Localization
gl

Optional

Parameter defines the country to use for the Google Hotels search. It's a two-letter country code. (e.g., us for the United States, uk for United Kingdom, or fr for France) Head to the Google countries page for a full list of supported Google countries.

hl

Optional

Parameter defines the language to use for the Google Hotels search. It's a two-letter language code. (e.g., en for English, es for Spanish, or fr for French). Head to the Google languages page for a full list of supported Google languages.

currency

Optional

Parameter defines the currency of the returned prices. Default to USD. Head to the Google Travel Currencies page for a full list of supported currency codes.

Advanced Parameters
check_in_date

Required

Parameter defines the check-in date. The format is YYYY-MM-DD. e.g. 2025-07-08

check_out_date

Required

Parameter defines the check-out date. The format is YYYY-MM-DD. e.g. 2025-07-09

adults

Optional

Parameter defines the number of adults. Default to 2.

children

Optional

Parameter defines the number of children. Default to 0.

children_ages

Optional

Parameter defines the ages of children. The age range is from 1 to 17, with children who haven't reached 1 year old being considered as 1.

Example for single child only:
5

Example for multiple children (seperated by comma ,):
5,8,10

The number of children's ages specified must match the children.

Advanced Filters
sort_by

Optional

Parameter is used for sorting the results. Default is sort by Relevance.

Available options:
3 - Lowest price
8 - Highest rating
13 - Most reviewed

min_price

Optional

Parameter defines the lower bound of price range.

max_price

Optional

Parameter defines the upper bound of price range.

property_types

Optional

Parameter defines to include only certain type of property in the results. Head to the Google Hotels Property Types page for a full list of supported Hotels property types. For Vacation Rentals, please refer to the Google Vacation Rentals Property Types page for a full list of supported Vacation Rentals property types.

Example for single property type only:
17

Example for multiple property types (seperated by comma ,):
17,12,18

amenities

Optional

Parameter defines to include only results that offer specified amenities. Head to the Google Hotels Amenities page for a full list of supported Hotels amenities. For Vacation Rentals, please refer to the Google Vacation Rentals Amenities page for a full list of supported Vacation Rentals amenities.

Example for single amenity only:
35

Example for multiple amenities (seperated by comma ,):
35,9,19

rating

Optional

Parameter is used for filtering the results to certain rating.

Available options:
7 - 3.5+
8 - 4.0+
9 - 4.5+

Hotels Filters
brands

Optional

Parameter defines the brands where you want your search to be concentrated. ID values are accessible inside brands array, located in our JSON output (e.g. brands[0].id).

Example for single brand only:
33

Example for multiple brands (seperated by comma ,):
33,67,101

This parameter isn't available for Vacation Rentals.

hotel_class

Optional

Parameter defines to include only certain hotel class in the results.

Available options:
2 - 2-star
3 - 3-star
4 - 4-star
5 - 5-star

Example for single hotel class only:
2

Example for multiple hotel class (seperated by comma ,):
2,3,4

This parameter isn't available for Vacation Rentals.

free_cancellation

Optional

Parameter defines to show results that offer free cancellation.

This parameter isn't available for Vacation Rentals.

special_offers

Optional

Parameter defines to show results that have special offers.

This parameter isn't available for Vacation Rentals.

eco_certified

Optional

Parameter defines to show results that are eco certified.

This parameter isn't available for Vacation Rentals.

Vacation Rentals Filters
vacation_rentals

Optional

Parameter defines to search for Vacation Rentals results. Default search is for Hotels.

bedrooms

Optional

Parameter defines the minimum number of bedrooms. Default to 0.

This parameter only available for Vacation Rentals.

bathrooms

Optional

Parameter defines the minimum number of bathrooms. Default to 0.

This parameter only available for Vacation Rentals.

Pagination
next_page_token

Optional

Parameter defines the next page token. It is used for retrieving the next page results.

Property Details
property_token

Optional

Parameter is used to get property details which consists of name, address, phone, prices, nearby places, and etc. You can find property_token from Google Hotels Properties API.

Serpapi Parameters
engine

Required

Set parameter to google_hotels to use the Google Hotels API engine.

no_cache

Optional

Parameter will force SerpApi to fetch the Google Hotels results even if a cached version is already present. A cache is served only if the query and all parameters are exactly the same. Cache expires after 1h. Cached searches are free, and are not counted towards your searches per month. It can be set to false (default) to allow results from the cache, or true to disallow results from the cache. no_cache and async parameters should not be used together.

async

Optional

Parameter defines the way you want to submit your search to SerpApi. It can be set to false (default) to open an HTTP connection and keep it open until you got your search results, or true to just submit your search to SerpApi and retrieve them later. In this case, you'll need to use our Searches Archive API to retrieve your results. async and no_cache parameters should not be used together.

zero_trace

Optional

Enterprise only. Parameter enables ZeroTrace mode. It can be set to false (default) or true. Enable this mode to skip storing search parameters, search files, and search metadata on our servers. This may make debugging more difficult.

api_key

Required

Parameter defines the SerpApi private key to use.

output

Optional

Parameter defines the final output you want. It can be set to json (default) to get a structured JSON of the results, or html to get the raw html retrieved.

API Results
JSON Results
JSON output includes structured data for Properties and brands.

A search status is accessible through search_metadata.status. It flows this way: Processing -> Success || Error. If a search has failed, error will contain an error message. search_metadata.id is the search ID inside SerpApi.

HTML Results
This API does not have html response, just a text. search_metadata.prettify_html_file contains prettified version of result. It is displayed in playground.

API Examples
JSON structure overview
{
  "brands": [
    {
      "id": "Integer - ID of the brand",
      "name": "String - Name of the brand",
      // children can be null
      "children": [
        {
          "id": "Integer - ID of the child's brand",
          "name": "String - Name of the child's brand"
        }
      ]
    }
  ],
  "ads": [
    {
      "name": "String - Name of the ad property",
      "source": "String - Source of the ad property",
      "source_icon": "String - URL of the source's icon",
      "link": "String - URL of the source property's website",
      "property_token": "String - Property token to retrieve the details of the property",
      "serpapi_property_details_link": "String - SerpApi's endpoint for retrieving details of the property",
      "gps_coordinates": {
        "latitude": "Float - Latitude of the GPS Coordinates",
        "longitude": "Float - Longitude of the GPS Coordinates"
      },
      "hotel_class": "Integer - Hotel class of the property",
      "thumbnail": "String - URL of the thumbnail image",
      "overall_rating": "Float - Overall rating for the property",
      "reviews": "Integer - Total reviews for the property",
      "price": "String - Price per night formatted with currency",
      "extracted_price": "Float - Extracted price per night",
      "amenities": "Array - Amenities provided by the property (e.g. Free Wi-Fi, Free parking, Hot tub, Pools, Airport shuttle and many more)",
      "free_cancellation": "Boolean - Indicate if the property offers free cancellation"
    },
    ...
  ],
  "properties": [
    {
      "type": "String - Type of property (e.g. hotel or vacation rental)",
      "name": "String - Name of the property",
      "description": "String - Description of the property",
      "link": "String - URL of the property's website",
      "logo": "String - URL of the property's logo",
      "sponsored": "Boolean - Indicate if the property result is sponsored",
      "eco_certified": "Boolean - Indicate if the property is Eco-certified",
      "gps_coordinates": {
        "latitude": "Float - Latitude of the GPS Coordinates",
        "longitude": "Float - Langitude of the GPS Coordinates"
      },
      "check_in_time": "String - Check-in time of the property (e.g. 3:00 PM)",
      "check_out_time": "String - Check-out time of the property (e.g. 12:00 PM)",
      "rate_per_night": {
        "lowest": "String - Lowest rate per night formatted with currency",
        "extracted_lowest": "Float - Extracted lowest rate per night",
        "before_taxes_fees": "String - Rate per night before taxes and fees formatted with currency",
        "extracted_before_taxes_fees": "Float - Extracted rate per night before taxes and fees"
      },
      "total_rate": {
        "lowest": "String - Lowest total rate for the entire trip formatted with currency",
        "extracted_lowest": "Float - Extracted lowest total rate for the entire trip",
        "before_taxes_fees": "String - Total rate before taxes and fees for the entire trip formatted with currency",
        "extracted_before_taxes_fees": "Float - Extracted total rate before taxes and fees for the entire trip"
      },
      "prices": [
        {
          "source": "String - Source of the site that list the price",
          "logo": "String - URL of the source's logo",
          "rate_per_night": {
            "lowest": "String - Lowest rate per night formatted with currency",
            "extracted_lowest": "Float - Extracted lowest rate per night",
            "before_taxes_fees": "String - Rate per night before taxes and fees formatted with currency",
            "extracted_before_taxes_fees": "Float - Extracted rate per night before taxes and fees"
          }
        }
      ],
      "nearby_places": [
        {
          "name": "String - Name of the place",
          "transportations": [
            {
              "type": "String - Type of transportation (e.g. Taxi, Walking, Public transport)",
              "duration": "String - Travel duration (e.g. 30 min)"
            }
          ]
        }
      ],
      "hotel_class": "String - Hotel class of the property (e.g. 5-star hotel)",
      "extracted_hotel_class": "Integer - Extracted hotel class of the property (e.g. 5)",
      "images": [
        {
          "thumbnail": "String - URL of the thumbnail",
          "original_image": "String - URL of the original image"
        }
      ],
      "overall_rating": "Float - Overall rating for the property",
      "reviews": "Integer - Total reviews for the property",
      "ratings": [
        {
          "stars": "Integer - Number of stars from 1 to 5",
          "count": "Integer - Total number of reviews for given star"
        }
      ],
      "location_rating": "Float - Location rating of the property (e.g. 1.8 is Bad location, 4.8 is excellent location)",
      "reviews_breakdown": [
        {
          "name": "String - Name of the review breakdown category",
          "description": "String - Description of the category",
          "total_mentioned": "Integer - Total mentioned about the category",
          "positive": "Integer - Total amount of positivity",
          "negative": "Integer - Total amount of negativity",
          "neutral": "Integer - Total amount of neutrality"
        }
      ],
      "amenities": "Array - Amenities provided by the property (e.g. Free Wi-Fi, Free parking, Hot tub, Pools, Airport shuttle and many more)",
      "excluded_amenities": "Array - Excluded amenities (e.g. No air conditioning, No airport shuttle, No beach access, Not pet-friendly and many more)",
      // For vacation rental property
      "essential_info": "Array - Essential info of the property (e.g. Entire villa, Sleeps 4, 9 bedrooms, 7 bathrooms)",
      "property_token": "String - Property token to retrieve the details of the property",
      "serpapi_property_details_link": "String - SerpApi's endpoint for retrieving details of the property"
    },
    ...
  ],
  "serpapi_pagination": {
    "current_from": "Integer - Current page start index",
    "current_to": "Integer - Current page end index",
    "next_page_token": "String - Next page token",
    "next": "String - SerpApi's Google Hotels API endpoint for the next page"
  }
}
Example with
q
:
Bali Resorts
GET


https://serpapi.com/search.json?engine=google_hotels&q=Bali+Resorts&check_in_date=2025-07-08&check_out_date=2025-07-09&adults=2&currency=USD&gl=us&hl=en

Code to integrate


Ruby

require 'google_search_results'

params = {
  engine: "google_hotels",
  q: "Bali Resorts",
  check_in_date: "2025-07-08",
  check_out_date: "2025-07-09",
  adults: "2",
  currency: "USD",
  gl: "us",
  hl: "en",
  api_key: "baebbb17f7e7cb99795eb830db62a9bd54e5cf6106b61984c64a571bf586744f"
}

search = GoogleSearch.new(params)
hash_results = search.get_hash

JSON Example

{
  "search_metadata": {
    "id": "6839b8b3fe1c6b28a63adfeb",
    "status": "Success",
    "json_endpoint": "https://serpapi.com/searches/53ea218ec31fbf8e/6839b8b3fe1c6b28a63adfeb.json",
    "created_at": "2025-05-30 13:54:59 UTC",
    "processed_at": "2025-05-30 13:54:59 UTC",
    "google_hotels_url": "https://www.google.com/_/TravelFrontendUi/data/batchexecute?rpcids=AtySUc&source-path=/travel/search&hl=en&gl=us&rt=c&soc-app=162&soc-platform=1&soc-device=1",
    "raw_html_file": "https://serpapi.com/searches/53ea218ec31fbf8e/6839b8b3fe1c6b28a63adfeb.html",
    "prettify_html_file": "https://serpapi.com/searches/53ea218ec31fbf8e/6839b8b3fe1c6b28a63adfeb.prettify",
    "total_time_taken": 2.71
  },
  "search_parameters": {
    "engine": "google_hotels",
    "q": "bali Resorts",
    "gl": "us",
    "hl": "en",
    "currency": "USD",
    "check_in_date": "2025-05-31",
    "check_out_date": "2025-06-01",
    "adults": 2,
    "children": 0
  },
  "search_information": {
    "total_results": 15000
  },
  "brands": [
    {
      "id": 33,
      "name": "Accor Live Limitless",
      "children": [
        {
          "id": 67,
          "name": "Banyan Tree"
        },
        {
          "id": 101,
          "name": "Grand Mercure"
        },
        {
          "id": 21,
          "name": "Ibis"
        },
        ...
      ]
    },
    {
      "id": 229,
      "name": "Aston"
    },
    {
      "id": 18,
      "name": "Best Western International",
      "children": [
        {
          "id": 155,
          "name": "Best Western"
        },
        {
          "id": 105,
          "name": "Best Western Premier"
        }
      ]
    },
    ...
  ],
  "ads": [
    {
      "name": "Ramada by Wyndham Bali Sunset Road Kuta",
      "source": "Hotels.com",
      "source_icon": "https://www.gstatic.com/travel-hotels/branding/f358dd45-ebd1-4af8-988d-d53154b73975.png",
      "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwicm9SVrMuNAxVoLdQBHSUOAXEYABACGgJvYQ&co=1&gclid=EAIaIQobChMInJvUlazLjQMVaC3UAR0lDgFxEA0YASACEgJ3ZfD_BwE&category=acrcp_v1_48&sig=AOD64_3nVPehFrq3HaUhmJ7RjPvZcAhSSA&adurl=",
      "property_token": "CgsIubu64M2bpKf9ARAB",
      "serpapi_property_details_link": "https://serpapi.com/search.json?adults=2&check_in_date=2025-05-31&check_out_date=2025-06-01&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&property_token=CgsIubu64M2bpKf9ARAB&q=bali+Resorts",
      "gps_coordinates": {
        "latitude": -8.704044999999999,
        "longitude": 115.18169499999999
      },
      "hotel_class": 4,
      "thumbnail": "https://lh3.googleusercontent.com/proxy/in1aa-T5B9UmNoPqJPtwRi2ShWK7yqg9Rc2kkFTCY5ckpKjoXpgLnGHRlTFJjfdZrNJrEY44RcFvfnLL2drgttG_8KGUH_01Qb5ZqvkCRiE958ngYIxLm3bKgEs2UeevEqVKjzXO_sTPrXLw4vx_dHyvXSQRoiU=w225-h150-k-no",
      "overall_rating": 4.2,
      "reviews": 3413,
      "price": "$39",
      "extracted_price": 39,
      "amenities": [
        "Hot tub",
        "Spa",
        "Pool",
        "Child-friendly",
        "Restaurant",
        "Bar",
        "Room service",
        "Airport shuttle",
        "Fitness centre",
        "Outdoor pool",
        "Free breakfast",
        "Air conditioning"
      ],
      "free_cancellation": true
    },
    {
      "name": "The Kenran Resort Ubud By Soscomma",
      "source": "Booking.com",
      "source_icon": "https://www.gstatic.com/travel-hotels/branding/icon_184.png",
      "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwicm9SVrMuNAxVoLdQBHSUOAXEYABAFGgJvYQ&co=1&gclid=EAIaIQobChMInJvUlazLjQMVaC3UAR0lDgFxEA0YAiACEgIzDvD_BwE&category=acrcp_v1_48&sig=AOD64_3kLBGTjyPFeCwAP1BYk_Q-7yQ2wA&adurl=",
      "property_token": "CgoI3o3r3u_PmOY4EAE",
      "serpapi_property_details_link": "https://serpapi.com/search.json?adults=2&check_in_date=2025-05-31&check_out_date=2025-06-01&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&property_token=CgoI3o3r3u_PmOY4EAE&q=bali+Resorts",
      "gps_coordinates": {
        "latitude": -8.473657,
        "longitude": 115.28599899999999
      },
      "hotel_class": 5,
      "thumbnail": "https://lh6.googleusercontent.com/proxy/xXNS-97PNyG0bg7UiKctU5JnluZv0_ELrD2c88tBU0v3BfMaczFVijGEy2D9Xn4Aer_CtOwvRylbD6UyzJjybFfYrTFI7UOwxnNEac9IWRPqx5-F-5qgp5GwdCWgR8nRreLEfweYuSGQ2f2PuUKXfoHSDytknT4=w339-h150-k-no",
      "overall_rating": 4.3,
      "reviews": 705,
      "price": "$130",
      "extracted_price": 130,
      "amenities": [
        "Spa",
        "Pool",
        "Restaurant",
        "Bar",
        "Room service",
        "Airport shuttle",
        "Fitness centre",
        "Outdoor pool",
        "Air conditioning"
      ]
    },
    ...
  ],
  "properties": [
    {
      "type": "vacation rental",
      "name": "Le Sabot Ubud",
      "link": "http://www.tiket.com/hotel/indonesia/le-sabot-bali-803001741836003177",
      "property_token": "ChoQ5YiTp-rKmO60ARoNL2cvMTFzc2djMTNqcRAC",
      "serpapi_property_details_link": "https://serpapi.com/search.json?adults=2&check_in_date=2025-05-31&check_out_date=2025-06-01&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&property_token=ChoQ5YiTp-rKmO60ARoNL2cvMTFzc2djMTNqcRAC&q=bali+Resorts",
      "gps_coordinates": {
        "latitude": -8.509233474731445,
        "longitude": 115.25044250488281
      },
      "rate_per_night": {
        "lowest": "$64",
        "extracted_lowest": 64,
        "before_taxes_fees": "$53",
        "extracted_before_taxes_fees": 53
      },
      "total_rate": {
        "lowest": "$64",
        "extracted_lowest": 64,
        "before_taxes_fees": "$53",
        "extracted_before_taxes_fees": 53
      },
      "prices": [
        {
          "source": "Tiket.com",
          "logo": "https://www.gstatic.com/travel-hotels/branding/be7f980c-6153-4e5f-a4f8-03adb19764e9.png",
          "num_guests": 2,
          "rate_per_night": {
            "lowest": "$64",
            "extracted_lowest": 64,
            "before_taxes_fees": "$53",
            "extracted_before_taxes_fees": 53
          }
        }
      ],
      "nearby_places": [
        {
          "name": "I Gusti Ngurah Rai International Airport",
          "transportations": [
            {
              "type": "Taxi",
              "duration": "1 hr 8 min"
            },
            {
              "type": "Public transport",
              "duration": "2 hr 9 min"
            }
          ]
        },
        {
          "name": "KEMULAN Kitchen & Culture",
          "transportations": [
            {
              "type": "Walking",
              "duration": "3 min"
            }
          ]
        }
      ],
      "images": [
        {
          "thumbnail": "https://lh5.googleusercontent.com/proxy/Aj3Z31i4VLvjkmIHcpEmcbfFjNRzpyMoq7rhDNdY-GNXICYbgNeFPLu2vMWMlB38esKsSNrWs-ikFpV1-fRKSn-7Vk4fX269KVZ7J4OJ1FzXZe1ZvR_1-oOByz0warcXstsAIRdHUEw5WO6nPwBMTKOS9RsvOw=s287-w287-h192-n-k-no-v1",
          "original_image": "https://s-light.tiket.photos/t/01E25EBZS3W0FY9GTG6C42E1SE/t_htl-dskt/tix-hotel/images-web/2021/04/20/f65e5ded-a3da-4d42-b054-d9e50ad5b942-1618902072410-256eba317efa4928ee8c51be3d1206d5.jpg"
        },
        {
          "thumbnail": "https://lh6.googleusercontent.com/proxy/ch3prh0CggbtC7Dn_xLdLeCL2Wp7hTVfU_OsOysccrG0z7c5lvKMB-eGbH2w_TqtnaX70DGs6LU6kJD56qMcf_yQTjuoZtQ23vLRM_b7L95vxXb6p8Og0iMZ5QkZR4BR0J5TMooBzpyYg93v4rsaDrHjllUWSg=s287-w287-h192-n-k-no-v1",
          "original_image": "https://s-light.tiket.photos/t/01E25EBZS3W0FY9GTG6C42E1SE/t_htl-dskt/tix-hotel/images-web/2023/07/31/577af768-0d22-4a40-b8e7-22d04e73ae29-1690794370431-eb0c0bed130c3909c0b6b86cb0e3047e.jpg"
        },
        ...
      ],
      "overall_rating": 4.441,
      "reviews": 78,
      "location_rating": 4,
      "amenities": [
        "Airport shuttle",
        "Balcony",
        "Pet-friendly"
      ],
      "excluded_amenities": [
        "No air conditioning",
        "No elevator",
        "No kitchen",
        "No microwave",
        "No cable TV",
        "Not wheelchair accessible"
      ],
      "essential_info": [
        "Entire villa",
        "Sleeps 20",
        "1 bedroom",
        "269 sq ft"
      ]
    },
    {
      "type": "vacation rental",
      "name": "Green Space Villa",
      "property_token": "ChkQxMvj5KCnqtYDGg0vZy8xMWtqNW1wbWZ0EAI",
      "serpapi_property_details_link": "https://serpapi.com/search.json?adults=2&check_in_date=2025-05-31&check_out_date=2025-06-01&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&property_token=ChkQxMvj5KCnqtYDGg0vZy8xMWtqNW1wbWZ0EAI&q=bali+Resorts",
      "gps_coordinates": {
        "latitude": -8.541170120239258,
        "longitude": 115.2611312866211
      },
      "check_in_time": "2:00 PM",
      "check_out_time": "12:00 PM",
      "rate_per_night": {
        "lowest": "$71",
        "extracted_lowest": 71,
        "before_taxes_fees": "$59",
        "extracted_before_taxes_fees": 59
      },
      "total_rate": {
        "lowest": "$71",
        "extracted_lowest": 71,
        "before_taxes_fees": "$59",
        "extracted_before_taxes_fees": 59
      },
      "prices": [
        {
          "source": "Tiket.com",
          "logo": "https://www.gstatic.com/travel-hotels/branding/be7f980c-6153-4e5f-a4f8-03adb19764e9.png",
          "num_guests": 2,
          "rate_per_night": {
            "lowest": "$71",
            "extracted_lowest": 71,
            "before_taxes_fees": "$59",
            "extracted_before_taxes_fees": 59
          }
        }
      ],
      "nearby_places": [
        {
          "name": "I Gusti Ngurah Rai International Airport",
          "transportations": [
            {
              "type": "Taxi",
              "duration": "59 min"
            }
          ]
        },
        {
          "name": "Warung Iga Bakar Gung Vedel",
          "transportations": [
            {
              "type": "Walking",
              "duration": "1 min"
            }
          ]
        }
      ],
      "images": [
        {
          "thumbnail": "https://lh4.googleusercontent.com/proxy/V30MeKD5dhyMtospBzi6EZxc7x5238qIlrI62q0Re1mLZG5Epa8_bdAZ3CUi6IiPpJ1hxTCTJHZHHg-xwFmfPfjcQULMgP-yqyvfU5y2UY-oYcPHcM64F88OVhnx2TbDA4Ql6O8aOrDV_rwi5df-EOFWk1j1Lw=s287-w287-h192-n-k-no-v1",
          "original_image": "https://s-light.tiket.photos/t/01E25EBZS3W0FY9GTG6C42E1SE/t_htl-dskt/tix-hotel/images-web/2024/03/08/2522914c-5dd9-47b1-9ff2-d74cd4f9d6a9-1709911501750-7a426cb3a67affa9a5ee10de2a6d0e76.jpg"
        },
        {
          "thumbnail": "https://lh5.googleusercontent.com/proxy/AIJcrHBZSbM-zWnA65or_r_RKJpSioi4O-GraplsOPrDgmBM4D1FeWy2rZ1rQ2IAh3GhOAGd93FUrdq2ZjTyMg9mXWF2AwG5-LuM-eXdWgIgIe67KIjWboZ8aY5aEgyPMhRQh9jv7KWkK6cZRMH-0bG5F5Th5g=s287-w287-h192-n-k-no-v1",
          "original_image": "https://p.fih.io/v2/nSr0o-3gbZN8o1xMecXCcG-BkDeQVo3k-wOeVogkTe7ajuFOX7O-WA8aRWhXz1jsToZif_TsA_xCWfhWRa0ZrMKqgSs36SAlP0uffaZ66SrFpFv8ArX-4wnSMZWkpp_sEld-8JTNFHbwITF4en3ketkYyx1j1dLbUfhlOgkNcIcn9PwNtk_AU2csbUk6dd9sEIgtPWr2pQoMEqcf5fQOj4gVcYQwOAM6IiyYD4BSyNyblRtH2nCutuIacvXA9EltddFd0EQk0IHphIg_aV-8ws64z7zUYWZqs_1Xqu-MVVg4FC5rXyOPY-oVVp1_aSJpuTZ4YgqHXBxG3hiorNLSgE0cJiM-"
        },
        ...
      ],
      "overall_rating": 4.4469004,
      "reviews": 342,
      "location_rating": 3.2,
      "amenities": [
        "Air conditioning",
        "Airport shuttle",
        "Outdoor pool",
        "Smoke-free",
        "Cable TV",
        "Free parking",
        "Free Wi-Fi"
      ],
      "excluded_amenities": [
        "No balcony",
        "No beach access",
        "No elevator",
        "No fireplace",
        "No fitness center",
        "No hot tub",
        "No indoor pool",
        "No kitchen",
        "No microwave",
        "Not pet-friendly",
        "Not wheelchair accessible"
      ],
      "essential_info": [
        "Entire cottage",
        "Sleeps 4",
        "2 bedrooms",
        "377 sq ft"
      ]
    },
    {
      "type": "vacation rental",
      "name": "Umasari Rice Terrace Villa by AGATA",
      "link": "https://www.bluepillow.com/search/5943983f7c00cb0e643ca28f?dest=bkng&cat=Villa&p_id=589de4307c00cb10c8d93176",
      "property_token": "ChoQ8PTfq-C2h-PIARoNL2cvMTF2NXJoMnJncRAC",
      "serpapi_property_details_link": "https://serpapi.com/search.json?adults=2&check_in_date=2025-05-31&check_out_date=2025-06-01&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&property_token=ChoQ8PTfq-C2h-PIARoNL2cvMTF2NXJoMnJncRAC&q=bali+Resorts",
      "gps_coordinates": {
        "latitude": -8.525629997253418,
        "longitude": 115.16854095458984
      },
      "check_in_time": "2:00 PM",
      "check_out_time": "12:00 PM",
      "rate_per_night": {
        "lowest": "$27",
        "extracted_lowest": 27,
        "before_taxes_fees": "$27",
        "extracted_before_taxes_fees": 27
      },
      "total_rate": {
        "lowest": "$27",
        "extracted_lowest": 27,
        "before_taxes_fees": "$27",
        "extracted_before_taxes_fees": 27
      },
      "prices": [
        {
          "source": "Bluepillow.com",
          "logo": "https://www.gstatic.com/travel-hotels/branding/190ff319-d0fd-4c45-bfc8-bad6f5f395f2.png",
          "num_guests": 2,
          "rate_per_night": {
            "lowest": "$27",
            "extracted_lowest": 27
          }
        }
      ],
      "nearby_places": [
        {
          "name": "I Gusti Ngurah Rai International Airport",
          "transportations": [
            {
              "type": "Taxi",
              "duration": "1 hr 12 min"
            }
          ]
        },
        {
          "name": "Nami Rasa Restaurant"
        }
      ],
      "images": [
        {
          "thumbnail": "https://lh3.googleusercontent.com/proxy/nVZEnpFKokz15zbmokDRucVDCcl5Bdjdo0oS8iEjkztVzutDswtSOna59X-IEduq9vQ4TJGtzDuRrseq9Ttcqqj1oifkazBPPgLiJUMyVatEnbHp-UJhKcVPy0Mpz_MFaPfPkKiSkiU-aZrXHbWVGqaZF1AX9uE=s287-w287-h192-n-k-no-v1",
          "original_image": "https://q-xx.bstatic.com/xdata/images/hotel/max1440x1080/322416801.jpg?k=7156a2d4aa18690537c2cd63d98c43d609637f6dd345f86247fafc4a49ca6073&o="
        },
        {
          "thumbnail": "https://lh3.googleusercontent.com/proxy/_4zBhPiHNIG5_sAasuVQwOfWQEfjhYWe_-BQxBxgTMSgje80yKJL7Kt8gKGmIkCPyzArMJ8zDbJdXtV-wztt2tLAi2k2UytToYcu9c4m-DxKZ6qWYmqut-BH4nkAMvLmGti4h93_XLCtnu8hN7VbxT5POC10YQ=s287-w287-h192-n-k-no-v1",
          "original_image": "https://q-xx.bstatic.com/xdata/images/hotel/max1440x1080/251073483.jpg?k=90f3d166d3e1ef559ee319f3b9a00ceb79bbf8af1cb2e50d600568a4cf714c6a&o="
        },
        ...
      ],
      "overall_rating": 4.5,
      "reviews": 512,
      "location_rating": 2.6,
      "amenities": [
        "Air conditioning",
        "Airport shuttle",
        "Beach access",
        "Kid-friendly",
        "Crib",
        "Elevator",
        "Indoor pool",
        "Ironing board",
        "Kitchen",
        "Outdoor pool",
        "Patio",
        "Smoke-free",
        "Cable TV",
        "Washer",
        "Wheelchair accessible",
        "Free parking",
        "Free Wi-Fi"
      ],
      "essential_info": [
        "Entire villa",
        "Sleeps 15",
        "9 bedrooms",
        "9 bathrooms",
        "11 beds"
      ]
    },
    ...
  ],
  "serpapi_pagination": {
    "current_from": 1,
    "current_to": 20,
    "next_page_token": "CBI=",
    "next": "https://serpapi.com/search.json?adults=2&check_in_date=2025-07-08&check_out_date=2025-07-09&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&next_page_token=CBI%3D&q=Bali+Resorts"
  }
}
Example
Vacation Rentals
with
q
:
Bali
GET


https://serpapi.com/search.json?engine=google_hotels&q=Bali&vacation_rentals=true&check_in_date=2025-07-08&check_out_date=2025-07-09&adults=2&currency=USD&gl=us&hl=en

Code to integrate


Ruby

require 'google_search_results'

params = {
  engine: "google_hotels",
  q: "Bali",
  vacation_rentals: "true",
  check_in_date: "2025-07-08",
  check_out_date: "2025-07-09",
  adults: "2",
  currency: "USD",
  gl: "us",
  hl: "en",
  api_key: "baebbb17f7e7cb99795eb830db62a9bd54e5cf6106b61984c64a571bf586744f"
}

search = GoogleSearch.new(params)
hash_results = search.get_hash

JSON Example

{
  "search_metadata": {
    "id": "655335bab68f8b5cf2b314a3",
    "status": "Success",
    "json_endpoint": "https://serpapi.com/searches/7e9e85e70fe7f094/655335bab68f8b5cf2b314a3.json",
    "created_at": "2023-11-14 08:54:18 UTC",
    "processed_at": "2023-11-14 08:54:18 UTC",
    "google_hotels_url": "https://www.google.com/_/TravelFrontendUi/data/batchexecute?rpcids=AtySUc&source-path=/travel/search&hl=en&gl=us&rt=c&soc-app=162&soc-platform=1&soc-device=1",
    "raw_html_file": "https://serpapi.com/searches/7e9e85e70fe7f094/655335bab68f8b5cf2b314a3.html",
    "prettify_html_file": "https://serpapi.com/searches/7e9e85e70fe7f094/655335bab68f8b5cf2b314a3.prettify",
    "total_time_taken": 3.34
  },
  "search_parameters": {
    "engine": "google_hotels",
    "q": "Bali",
    "gl": "us",
    "hl": "en",
    "currency": "USD",
    "check_in_date": "2025-07-08",
    "check_out_date": "2025-07-09",
    "adults": 2,
    "children": 0,
    "vacation_rentals": true
  },
  "search_information": {
    "total_results": 14920
  },
  "properties": [
    {
      "type": "vacation rental",
      "name": "Yana Villas Kemenuh",
      "gps_coordinates": {
        "latitude": -8.555330276489258,
        "longitude": 115.28772735595703
      },
      "check_in_time": "2:00 PM",
      "check_out_time": "12:00 AM",
      "rate_per_night": {
        "lowest": "$40",
        "extracted_lowest": 40,
        "before_taxes_fees": "$33",
        "extracted_before_taxes_fees": 33
      },
      "total_rate": {
        "lowest": "$202",
        "extracted_lowest": 202,
        "before_taxes_fees": "$167",
        "extracted_before_taxes_fees": 167
      },
      "prices": [
        {
          "source": "Bluepillow.com",
          "logo": "https://www.gstatic.com/travel-hotels/branding/190ff319-d0fd-4c45-bfc8-bad6f5f395f2.png",
          "rate_per_night": {
            "lowest": "$40",
            "extracted_lowest": 40,
            "before_taxes_fees": "$33",
            "extracted_before_taxes_fees": 33
          }
        }
      ],
      "nearby_places": [
        {
          "name": "I Gusti Ngurah Rai International Airport",
          "transportations": [
            {
              "type": "Taxi",
              "duration": "58 min"
            },
            {
              "type": "Public transport",
              "duration": "2 hr 22 min"
            }
          ]
        },
        {
          "name": "Warung Thepaon",
          "transportations": [
            {
              "type": "Taxi",
              "duration": "10 min"
            }
          ]
        }
      ],
      "images": [
        {
          "thumbnail": "https://lh4.googleusercontent.com/proxy/1DpPI6Ipxyb3hCE5eBcnPWRiMvGGSgu-h50VkgCT_1ooT9mIPUIP2PvnfVHtHKpVCMJ6eG5x-lsYZRy4_cVg74cgY5qvDp-toQeT9bhkaSv15tUpFqVz8B0hr4JPdDsb6q-3Y_XJRhZmMuFVvLd0RU5Kg7GDqww=s287-w287-h192-n-k-no-v1",
          "original_image": "https://q-xx.bstatic.com/xdata/images/hotel/max1440x1080/223247563.jpg?k=17e4b19b4710d224007544d313b2e012e33475d53877bdea8cf036d8f6a60c1c&o="
        },
        {
          "thumbnail": "https://lh4.googleusercontent.com/proxy/HDK_ROG3ZEbuBkU5LEh2GIhGoiVm3Eof-1OBgO_50NdTLMh0BJ0W9r4scwbIi2bD53V897tTaTKYLP345Sf397KHtGijMdc2oFJuxdYGyygFwYECxX_88F8M38fjic99TnEJhqpXf1aNt_pV2uXDJD7K-ncqAA=s287-w287-h192-n-k-no-v1",
          "original_image": "https://q-xx.bstatic.com/xdata/images/hotel/max1440x1080/223247466.jpg?k=4bcc896b368c2bf0fc74edf39003f4ae18889e27d7c6df3d8ade34be887986be&o="
        },
        {
          "thumbnail": "https://lh6.googleusercontent.com/proxy/LRDW9oGz8oY9Pzis9Nli9yvOULgbnSqHd8tsg4mwHwLpBvCcm08r8F8xzFl9q5gymyiKlzBNNXdOqXPRR_mmBQndFePSlxDJcI7NSdSXR6wu8o3i-E7-nZiRnPJ2-BSmBpI8EDFMZjDBOkIBbRYcWfYP76b29g=s287-w287-h192-n-k-no-v1",
          "original_image": "https://s-light.tiket.photos/t/01E25EBZS3W0FY9GTG6C42E1SE/t_htl-dskt/tix-hotel/images-web/2020/10/31/9e51d564-cc30-4a2a-ab14-809d6deede87-1604146952201-3950d28982374ab237d1e13478487cd9.jpg"
        },
        ...
      ],
      "overall_rating": 3.994737,
      "reviews": 152,
      "location_rating": 3.3,
      "amenities": [
        "Air conditioning",
        "Airport shuttle",
        "Balcony",
        "Crib",
        "Fitness center",
        "Outdoor pool",
        "Smoke-free",
        "Washer",
        "Free parking",
        "Free Wi-Fi"
      ],
      "excluded_amenities": [
        "No beach access",
        "Not kid-friendly",
        "No elevator",
        "No fireplace",
        "No heating",
        "No hot tub",
        "No indoor pool",
        "No ironing board",
        "No kitchen",
        "No microwave",
        "No outdoor grill",
        "No oven stove",
        "No patio",
        "Not wheelchair accessible"
      ],
      "essential_info": [
        "Entire house",
        "Sleeps 2",
        "1 bedroom",
        "1 bathroom",
        "1 bed",
        "215 sq ft"
      ],
      "property_token": "ChcIyo2FjenOdOasxGgsvZy8xdGYyMTV2aBAB",
      "serpapi_property_details_link": "https://serpapi.com/search.json?adults=2&check_in_date=2025-05-30&check_out_date=2025-05-31&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&property_token=ChkItJPPiMiRmvNsGg0vZy8xMWJ5Y2djeGszEAE&q=Bali+Resorts"
    },
    {
      "type": "vacation rental",
      "name": "Tirta sari",
      "gps_coordinates": {
        "latitude": -8.416190147399902,
        "longitude": 115.2825698852539
      },
      "check_in_time": "1:00 PM",
      "check_out_time": "6:00 AM",
      "rate_per_night": {
        "lowest": "$50",
        "extracted_lowest": 50,
        "before_taxes_fees": "$42",
        "extracted_before_taxes_fees": 42
      },
      "total_rate": {
        "lowest": "$252",
        "extracted_lowest": 252,
        "before_taxes_fees": "$208",
        "extracted_before_taxes_fees": 208
      },
      "prices": [
        {
          "source": "Bluepillow.com",
          "logo": "https://www.gstatic.com/travel-hotels/branding/190ff319-d0fd-4c45-bfc8-bad6f5f395f2.png",
          "rate_per_night": {
            "lowest": "$50",
            "extracted_lowest": 50,
            "before_taxes_fees": "$42",
            "extracted_before_taxes_fees": 42
          }
        }
      ],
      "nearby_places": [
        {
          "name": "I Gusti Ngurah Rai International Airport",
          "transportations": [
            {
              "type": "Taxi",
              "duration": "1 hr 35 min"
            }
          ]
        },
        ...
      ],
      "images": [
        {
          "thumbnail": "https://lh6.googleusercontent.com/proxy/HfsdZpRpkAEHaei8gnPjCRbdwsd_EDHupUGPzYmEC5YrCZFxOGoZS5xaiBb7qlTO-d7GMlmdpBM3U1mXlBZknrNYL1IWGAsDhF7bWaB95A1AW35m0YQSBIBR5rXLYHfL8g-7ymvrV-bNa7FtW5ox1LMdZBdJtwI=s287-w287-h192-n-k-no-v1",
          "original_image": "https://s-light.tiket.photos/t/01E25EBZS3W0FY9GTG6C42E1SE/t_htl-dskt/tix-hotel/images-web/2023/05/17/b14d0a14-388c-4eff-8cfa-71ba9665045c-1684315756338-947f4308781850dc6b18828071a0c6f3.jpg"
        },
        ...
      ],
      "overall_rating": 4.225,
      "reviews": 12,
      "location_rating": 3.6,
      "amenities": [
        "Air conditioning",
        "Balcony",
        "Crib"
      ],
      "excluded_amenities": [
        "No airport shuttle",
        "No beach access",
        "Not kid-friendly",
        ...
      ],
      "essential_info": [
        "Entire villa",
        "Sleeps 3",
        "1 bedroom",
        "1 bathroom",
        "269 sq ft"
      ],
      "property_token": "ChcIyo2FjenOuZ8xGgsvZy8xdGds4TV2aBAB",
      "serpapi_property_details_link": "https://serpapi.com/search.json?adults=2&check_in_date=2025-05-30&check_out_date=2025-05-31&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&property_token=ChYIoeT-jsbDiJI6GgovbS8wajYzcXAwEAE&q=Bali+Resorts"
    },
    {
      "type": "vacation rental",
      "name": "Keramas Sacred River Village",
      "link": "https://deals.vio.com?sig=73aca13c7f952d2641c156f3e69125e1eb497c325f122828ee5aa8797168b9a12d32303331333438363233&turl=https%3A%2F%2Fwww.vio.com%2FHotel%2FSearch%3FhotelId%3D5255198%26utm_source%3Dgha-vr%26utm_campaign%3Dstatic%26openHotelDetails%3D1",
      "gps_coordinates": {
        "latitude": -8.586440086364746,
        "longitude": 115.3296127319336
      },
      "check_in_time": "2:00 PM",
      "check_out_time": "12:30 AM",
      "rate_per_night": {
        "lowest": "$46",
        "extracted_lowest": 46,
        "before_taxes_fees": "$38",
        "extracted_before_taxes_fees": 38
      },
      "total_rate": {
        "lowest": "$228",
        "extracted_lowest": 228,
        "before_taxes_fees": "$188",
        "extracted_before_taxes_fees": 188
      },
      "prices": [
        {
          "source": "Vio.com",
          "logo": "https://www.gstatic.com/travel-hotels/branding/7287187d-2586-494f-92ff-726979e94c2a.png",
          "rate_per_night": {
            "lowest": "$46",
            "extracted_lowest": 46,
            "before_taxes_fees": "$38",
            "extracted_before_taxes_fees": 38
          }
        }
      ],
      "nearby_places": [
        {
          "name": "I Gusti Ngurah Rai International Airport",
          "transportations": [
            {
              "type": "Taxi",
              "duration": "52 min"
            }
          ]
        },
        {
          "name": "Warong Legong",
          "transportations": [
            {
              "type": "Taxi",
              "duration": "4 min"
            }
          ]
        }
      ],
      "images": [
        {
          "thumbnail": "https://lh5.googleusercontent.com/proxy/yXB-H-lTQ1MH1bWIMXAU3JRRJCiLC6apOl-dkE2FhpTQLljrYhEayGK0_a5hGaLnJlVpKh072yvLFV2mH-brVIpRGBBftAvu-d3bAbjHK9EKMmjzoARdCsUW_KnuvtIZwvC0r6DAyevg1JL2dDflEB2PBoV8qFE=s287-w287-h192-n-k-no-v1",
          "original_image": "https://p.fih.io/v2/nSr0o-3gbZN8o1xMecXCcG-BkDeQVo3k-wOeVogkTe7ajuFOX7O-WA8aRWhXz1jsToZif_TsA_xCWfhWRa0Z3Ke1vT1z90khCU2Da7x0-xiShVn8GuC9vj7KBaOhg-vgKl4c_rzAKF78OTF4en3ketkYyx1j1dLbUfhlOgkNcIcn9PwNtk_AU2csbUk6dd9sGqAEVmr2qjQMPI095Pdv3pEtFPIxOxxOPC-YWoFEg4yXvCZQ3nG9m-EOZqnW2lodL_hO30Ezy-jlqKVHa0uB_8O59smfYWZisPxpsuKafAZkFxNkAjW1f-Y-DpE9Rgh64AZ_KQd1YCIQC1WVxAG4bqbEaIBWIgb2"
        },
        {
          "thumbnail": "https://lh3.googleusercontent.com/proxy/K3K-ywMEqxZwT8DWkI4v8_qukJDwY01i8mOZDP6ppAlbh9GQcGotrQDWO0NSBo3GW5x_hXnxGGZpvBVCrsNtSfk10DEfSB4qYaybt5TLWvxjwPXrUQCEGqkKEHDdcTpSxGg8MvgmMe-GBrQLO0MjWLxn4XTO7LU=s287-w287-h192-n-k-no-v1",
          "original_image": "https://p.fih.io/v2/nSr0o-3gbZN8o1xMecXCcG-BkDeQVo3k-wOeVogkTe7ajuFOX7O-WA8aRWhXz1jsToZif_TsA_xCWfhWRa0ZrqOuunYD91xgFQ_ea84R1z7jkWbdLumZpU_AM4PivpuFGD9eyu67MlTVFzF4en3ketkYyx1j1dLbUfhlOgkNcIcn9PwNtk_AU2csbUk6dd9sGqAEVmr2qjQMPI095Pdv3pEtFPIxOxxOPC-YWoFEg4yXvCZQ3nG9m-EOZqnW2lodL_hO30Ezy-jlqKVHa0uB_8O59smfYWZisPxpsuKafAZiAxNnXzS1fLw-U5E9Rgh64AZ_KQd1YCKpLdhy5WGXi-CaBHchStHA"
        },
        {
          "thumbnail": "https://lh4.googleusercontent.com/proxy/Rm6W1Ti3m6XIgyV8UE786I_f4EPBIFcFesq8eJbgqc0sgv1G6bBwfzLK8FYO6jmW0idKZsfkL0Ozo43Fr8J0AVaCEAlh71GTZwfBgafPG-craBwN__kAGzd9KukM_HLyxLx1Qf9SQ5NvW9R7P5GwK4fkB8mowuI=s287-w287-h192-n-k-no-v1",
          "original_image": "https://p.fih.io/v2/nSr0o-3gbZN8o1xMecXCcG-BkDeQVo3k-wOeVogkTe7ajuFOX7O-WA8aRWhXz1jsToZif_TsA_xCWfhWRa0ZvcfmhAQK8GZjLRmGdIFV8DvNriDeH-2U-Dz7cr-i_Z-2KgB83r7cGl_FJTF4en3ketkYyx1j1dLbUfhlOgkNcIcn9PwNtk_AU2csbUk6dd9sGqAEVmr2qjQMPI095Pdv3pEtFPIxOxxOPC-YWoFEg4yXvCZQ3nG9m-EOZqnW2lodL_hO30Ezy-jlqKVHa0uB_8O59smfYWZisPxpsuKafAZkFy1rXyCmePQpaZE9Rgh64AZ_KQd1YCJpER13G6kZmqrt3sn5ocKZ"
        },
        ...
      ],
      "overall_rating": 4.35,
      "reviews": 152,
      "location_rating": 2.8,
      "amenities": [
        "Air conditioning",
        "Airport shuttle",
        "Outdoor pool",
        ...
      ],
      "excluded_amenities": [
        "No beach access",
        "No elevator",
        "No fireplace",
        ...
      ],
      "essential_info": [
        "Sleeps 10",
        "8 bedrooms",
        "5 bathrooms"
      ],
      "property_token": "ChcIyo2Fjdjs2uZ8xGgsvZy8xdGYyMTV2aBAB",
      "serpapi_property_details_link": "https://serpapi.com/search.json?adults=2&check_in_date=2025-05-30&check_out_date=2025-05-31&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&property_token=ChgIieDryrrojIO-ARoLL2cvMXg2bjRsYzIQAQ&q=Bali+Resorts"
    },
    ...
  ],
  "serpapi_pagination": {
    "current_from": 1,
    "current_to": 18,
    "next_page_token": "CBI=",
    "next": "https://serpapi.com/search.json?adults=2&check_in_date=2025-07-08&check_out_date=2025-07-09&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&next_page_token=CBI%3D&q=Bali&vacation_rentals=true"
  }
}
Example of showing property details with
q
 search
For certain searches with q, especially when q is the exact name of a hotel, Google Hotels may return the details of the single matching property instead of properties search results.

In such cases, search_information.hotels_results_state will have the value Showing results for property details.

Also serpapi_property_details_link will be present as a canonical way to retrieve the property details using property_token.

GET


https://serpapi.com/search.json?engine=google_hotels&q=H10+Port+Vell&check_in_date=2025-07-08&check_out_date=2025-07-09&adults=2&currency=USD&gl=us&hl=en

Code to integrate


Ruby

require 'google_search_results'

params = {
  engine: "google_hotels",
  q: "H10 Port Vell",
  check_in_date: "2025-07-08",
  check_out_date: "2025-07-09",
  adults: "2",
  currency: "USD",
  gl: "us",
  hl: "en",
  api_key: "baebbb17f7e7cb99795eb830db62a9bd54e5cf6106b61984c64a571bf586744f"
}

search = GoogleSearch.new(params)
hash_results = search.get_hash

JSON Example

{
  ...
  "search_information": {
    "hotels_results_state": "Showing results for property details"
  },
  "type": "hotel",
  "name": "H10 Port Vell",
  "description": "Across the street from a marina, this contemporary hotel is a 4-minute walk from a metro station, 4 km from Sagrada Família and 5 km from Park Güell. Streamlined, minimalist rooms feature free Wi-Fi and flat-screen TVs, as well as desks, Nespresso machines and minifridges. Upgraded rooms add private terraces or balconies. Room service is available. A breakfast buffet is complimentary. Other amenities include a chic restaurant, a cafeteria and a bar, plus a rooftop terrace. There's also a plunge pool and a fitness room.",
  "link": "https://www.h10hotels.com/en/barcelona-hotels/h10-port-vell?utm_source=google_my_business&utm_medium=boton_sitio_web&utm_campaign=hpv",
  "address": "Pas de Sota Muralla, 9, Ciutat Vella, 08003 Barcelona, Spain",
  "property_token": "ChgIjayklaXUgth3GgwvZy8xcHAydF9qdDEQAQ",
  "serpapi_property_details_link": "https://serpapi.com/search.json?adults=2&check_in_date=2025-05-30&check_out_date=2025-05-31&children=0&currency=USD&engine=google_hotels&gl=us&hl=en&property_token=ChcI9uq9hrWO2OtjGgsvZy8xMjJ0YzFteBAB&q=Bali+Resorts",
  "phone": "+34 933 10 30 65",
  "phone_link": "tel:+34933103065",
  "gps_coordinates": {
    "latitude": 41.381571799999996,
    "longitude": 2.1838414999999998
  },
  "check_in_time": "3:00 PM",
  "check_out_time": "12:00 PM",
  "rate_per_night": {
    "lowest": "$123",
    "extracted_lowest": 123,
    "before_taxes_fees": "$100",
    "extracted_before_taxes_fees": 100
  },
  "total_rate": {
    "lowest": "$123",
    "extracted_lowest": 123,
    "before_taxes_fees": "$100",
    "extracted_before_taxes_fees": 100
  },
  ...
}
