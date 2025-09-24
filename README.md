The project was divided into four parts -
Authorisation: Enabled different permissions for shopkeeper, admin and user
      urls:  'auth/user/signup/'
               'auth/user/login/'
               'auth/admin/login/'
               'auth/profile/'
               
Inventory:    You can create , update, read, delete (CRUD implementation) the inventory using this endpoint. Permissions only for shopkeepers. 
      urls:   'inventory/list/'  lists all objects in the inventory with its details
              'inventory/new/'   (POST method requires: the following fields: name,description,category,price,quantity) in JSON format
              'inventory/update/' (POST method requires id, can update any of the above fields also includes) in JSON format
              'inventory/restock/' (POST method requires id, adds the arrived stock to the quantity) in JSON format
              'inventory/orders/'  lists order by user
              'inventory/revenue/  gives the revenue statistics per month/ per year

Shop:        Users/shopkeepers can acess this endpoint 
      urls:   'shop/list/'  Presents the shopping items
              'shop/item/<int:item_id>/' Detailed information about a specific item
              'shop/categories/' lists all available categories
              
Order: Users can order new products,view past orders and find order details of a particular order
      urls: orders/past/' 
           'orders/new/' (POST method requires: the following fields: items:[list_of_items],shipping_adress,phone number,special_instructionss) in JSON format
           'orders/<int:order_id>'
