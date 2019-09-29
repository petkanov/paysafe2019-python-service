from flask_restful import Resource
from flask_jsonpify import jsonify
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

class User(Resource):
    def get(self, userId):
        
        connection = create_engine('mysql+pymysql://root:root@localhost:3306/walletbuddy').connect()
        # Extracting dataset for model training based on users in database except currently created
        # Since there is not enough data in database we don't want to mess up training results with
        # the data of the current users (only for demonstration, in reality dataset would be huge)
        dataset = pd.read_sql('select * from users_clustering_data where user_id<0', connection)
        X = dataset.iloc[:, [4,3,2] ].values

        dataset = pd.read_sql('select * from users_clustering_data where user_id=%s'%userId, connection)
        userData =  dataset.iloc[0,[4,3,2]].values

        # Taking care in case of NaN possible values
        from sklearn.impute import SimpleImputer
        imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
        X = imp_mean.fit_transform(X)

        #Extracting components which "most" represent the data in descending order of relevance 
        from sklearn.decomposition import PCA
        pca = PCA(n_components = 2)
        X = pca.fit_transform(X)
        userData = pca.transform(userData.reshape(-1, 1))
        
        # Using the elbow method to find the optimal number of clusters
        from sklearn.cluster import KMeans 
        # Fitting K-Means to the dataset and relating each User to a Cluster
        kmeans = KMeans(n_clusters = 5, init = 'k-means++', random_state = 0, max_iter=300, n_init=10)
        y_kmeans = kmeans.fit_predict(X)
        colors = {0:'black', 1:'blue', 2:'green', 3:'cyan', 4:'purple'}
        
        points = []
        for i in range(0,5):
            x = X[y_kmeans == i, 0]
            y = X[y_kmeans == i, 1]
            for j, row in enumerate(x):
                point = {"x":float(x[j]),"y":float(y[j]),"color":colors[i]}
                points.append(point)
            points.append( {"x":float(kmeans.cluster_centers_[i, 0]),"y":float(kmeans.cluster_centers_[i, 1]),"color":"yellow"} )
 
        points.append( {"x":float(userData[0][0]),"y":float(userData[0][1]),"color":"red"} )
        
        return jsonify(points)
		
