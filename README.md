# image-recog-api

The project is about the REST API using flask for image reoginition.

It has 3 resource:

  1)Register--- input(username,password).By default each user is provided with 4 tokens
  2)Classify--- input(username,password and image url) the image url provided will be downloaded and used as  an input to the classify_image.py image recogition tesr flow model.
                it will classify and provide the output as JSON file.Each time the user use the service, his token will be used.
                
  3)Refill---- input(username,admin password, token) The admin password login is used to recharge the expired token of the username.
  
  
  The project uses Docker tool to build and deploy
