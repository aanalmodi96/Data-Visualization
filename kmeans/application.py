from flask import Flask, redirect, render_template, request, make_response
import pymysql.cursors
import pandas as pd
import pylab as pl
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from collections import Counter, defaultdict
import math
import itertools
import time
import random

application= app = Flask(__name__)

endpoint = "rupin.caxeazea3so2.us-east-2.rds.amazonaws.com"
port = "3306"
user = "rupin"
password = "lucaslieva"
database = "rupin"


def connectDb():
    connection = pymysql.connect(host=endpoint,
                                 # port=port,
                                 user=user,
                                 password=password,
                                 db=database,
                                 local_infile=True
                                 )
    cursor = connection.cursor()
    return cursor


@application.route('/')
def index():
    return render_template('index.html')




@application.route('/kmeansClusteringCSV')
def kmeansClusteringCSV():

    numberOfClusters = int(request.args.get('cluster'))
    column1 = request.args.get('col1')
    column2 = request.args.get('col2')

    data_frame = pd.read_csv("titanic3.csv")
    img = BytesIO()
    data_frame.head()
    # data_frame[['Age', 'Fare']].hist()
    # plt.show()
    x = data_frame[[column1, column2]].fillna(0)
    x = np.array(x)
    print(x)

    kmeans = KMeans(n_clusters=numberOfClusters)

    kmeansoutput_x = kmeans.fit(x)
    centroid = kmeans.cluster_centers_
    print(type(kmeansoutput_x))

    pl.figure('5 Cluster K-Means')

    pl.scatter(x[:, 0], x[:, 1], cmap='rainbow')
    pl.scatter(centroid[:,0], centroid[:,1], marker="x", s=150, linewidths=5, zorder=10)

    pl.title('5 Cluster K-Means')
    pl.xlabel(column1)

    pl.ylabel(column2)

    # pl.show()

    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue())

    response = make_response(img.getvalue())
    response.headers['Content-Type'] = 'image/png'

    return response


@application.route('/kmeansClustering', methods=["GET","POST"])
def kmeansClustering():

    numberOfClusters = (int)(request.form['cluster'])
    column1 = request.form['col1']
    column2 = request.form['col2']
    cursor = connectDb()
    # select age,fare from aws.titanic3  WHERE(aws.titanic3.age IS NOT NULL AND aws.titanic3.fare IS NOT NULL );
    sql = "select {},{} from quiz5.titanic3 WHERE(quiz5.titanic3.{} IS NOT NULL AND quiz5.titanic3.{} IS NOT NULL );".format(column1,column2,column1,column2)
    print(sql)
    starttime = time.time()

    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    print(result)

    x = np.array(result)
    print(x)
    #
    kmeans = KMeans(n_clusters=numberOfClusters)
    #
    kmeansoutput_x = kmeans.fit(x)
    centroid = kmeans.cluster_centers_
    print(type(kmeansoutput_x))
    #
    count = Counter(kmeans.labels_)
    print("I'm cluster counter", count)
    clusters_indices = defaultdict(list)
    for index, c in enumerate(kmeans.labels_):
        clusters_indices[c].append(x[index])

    print(c , clusters_indices)
    count = Counter(kmeans.labels_)

    end_time = time.time()
    duration = end_time-starttime


    return render_template('clusters.html',centroid=centroid, ci=clusters_indices, totalPoints=count, time=duration)

@application.route('/DistanceCentroidPoints')
def DistanceCentroidPoints():

    numberOfClusters = int(request.args.get('numberOfClusters'))
    column1 = request.args.get('column1')
    column2 = request.args.get('column2')

    cursor = connectDb()
    sql = "select "+column1+", "+column2+" from quiz5.titanic3"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()



    x = np.array(result)


    kmeans = KMeans(n_clusters=numberOfClusters)

    kmeansoutput_x = kmeans.fit(x)
    centroid = kmeans.cluster_centers_



    count = Counter(kmeans.labels_)
    print("I'm cluster counter", count)

    dataPoints = []

    clusters_indices = defaultdict(list)
    for index, c in enumerate(kmeans.labels_):
        clusters_indices[c].append(x[index])
        dataPoints.append(x[index])
        print("im point :",x[index])

    print(clusters_indices)



    # for calculating distance
    dist_list = []
    cordinate1 = []
    cordinate2 = []
    for i in range(0, len(centroid) - 1):
        for j in range(i + 1, len(centroid)):
            x1 = centroid[i][0]
            x2 = centroid[j][0]
            y1 = centroid[i][1]
            y2 = centroid[j][1]
            temp = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)
            dist = math.sqrt(temp)

            dist_list.append(list(zip(centroid[i][:], centroid[j][:], itertools.repeat(dist))))

    print(dist_list)
    dist_len = len(dist_list)

    return render_template('maxdistance.html', ci=dist_list, totalPoints = dist_len)



if __name__ == '__main__':
    app.run(debug=True)
