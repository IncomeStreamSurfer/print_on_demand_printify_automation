First go to https://beta.dreamstudio.ai/account and get your secret key
Then go to openAI and get your secret key
Finally go to printify and get your secret key https://try.printify.com/vi2c7btfi5fq
Make a shopify development store shopify.pxf.io/anWAnR
Connect your Shopify store and Printify shop together
Get your Printify shop code Find your shop ID by running this in cmd: curl -X GET https://api.printify.com/v1/shops.json --header "Authorization: Bearer YOUR_SECRET_KEY"
Add the shop code to YOUR_SHOP_ID
Add the other secret keys where they need to be
Change the product, it's currently set to upload wall art 
To change the product you need the blueprint id and print provider, to get that go to Printify, go to the product you want, and get the two codes from the URL
Now you need the variant ID by running this into the cmd  curl -X GET "https://api.printify.com/v1/catalog/blueprints/1098/print_providers/228/variants.json" "Authorization: Bearer YOUR_PRINTIFY_KEY"
Now run python createimages.py
Now run uploadimages.py 

You're now done!
