from flask import Flask, request
import requests

store = 1
app = Flask(__name__)

def getAisle(prod_name):
  print("prod_name", prod_name)
  sku_ids = getSkuId(prod_name)
  aisle_name = ""
  for sku_id in sku_ids:
    aisle_name_obj_raw = requests.get('https://api.wegmans.io/products/'+str(sku_id)+'/locations/'+str(store)+'?api-version=2018-10-18&Subscription-Key=9acb204c806141c3afaae17c62ed4804')
    aisle_name_obj = aisle_name_obj_raw.json() 
    aisle_name_locs = aisle_name_obj["locations"]
    for location in aisle_name_locs:
      aisle_name = location["name"]
      break
    if aisle_name!= "":
      break
  
  if aisle_name != "":
    aisle_name = "You can find " +str(prod_name)+ " on the aisle "+ str(aisle_name)
  return aisle_name

def getSkuId(prod_name):
  sku_obj_raw = requests.get('https://api.wegmans.io/products/search?query='+str(prod_name)+'&results=5&page=1&api-version=2018-10-18&Subscription-Key=9acb204c806141c3afaae17c62ed4804')
  sku_obj = sku_obj_raw.json() 
  results = sku_obj["results"]
  sku_ids = []
  for result in results:
    sku_ids.append(result["sku"])
  return sku_ids

@app.route('/webhook', methods=['POST'])
def webhook():
   
   # call GET https://api.wegmans.io/products/search?query=beer&results=100&page=1&api-version=2018-10-18 HTTP/1.1 
   # to search product sku id 

   # call GET https://api.wegmans.io/products/621346/locations/1?api-version=2018-10-18 HTTP/1.1
   # use sku id to find location of searched product

    fulfilmentText = ""
    req = request.get_json(silent=True, force=True)
    queryRes = req.get("queryResult")
    print(queryRes)
    if queryRes.get("queryText") == "GOOGLE_ASSISTANT_WELCOME":
      fulfilmentText = "Welcome to Wegman's store! Please let me know what you're looking for"
    elif queryRes:
      param = queryRes.get("parameters")
    else:
      fulfilmentText = "Welcome to Wegman's store!"
      return {
          "payload": {
            "google": {
              "expectUserResponse": False,
              "richResponse": {
                "items": [
                  {
                    "simpleResponse": {
                      "textToSpeech": fulfilmentText,
                      "displayText": fulfilmentText
                    }
                  }
                ]
              }
            }
          }
        }

    prod_name = ""
    if fulfilmentText == "":
      if param.get("product_name"):
        prod_name = param.get("product_name")
        fulfilmentText = getAisle(prod_name)
      elif param.get("product_name") == "" and queryRes.get("queryText") != "":
        fulfilmentText = "Sorry, I couldn't get the name of the product. Can you please repeat?"

    if fulfilmentText == "":
      fulfilmentText = "Sorry, I couldn't get the name of the product. Can you please repeat?"

    return{
          "payload": {
            "google": {
              "expectUserResponse": True,
              "richResponse": {
                "items": [
                  {
                    "simpleResponse": {
                      "textToSpeech": fulfilmentText,
                      "displayText": fulfilmentText
                    }
                  }
                ]
              }
            }
          }
        }
        # sku id of req 
        # 2nd API call on sku id and store = 1 

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)