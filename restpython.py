from flask import Flask
from flask_restful import Api
from UsersCluster import User

app = Flask(__name__)
api = Api(app)
       
api.add_resource(User, '/user/<userId>')
 
if __name__ == '__main__':
     app.run(port='5002')