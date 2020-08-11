from flask import Flask,render_template,request
import mysqlconnect
import numpy as np
import random
import math
# from sklearn.cluster import KMeans


# EB looks for an 'application' callable by default.
application = Flask(__name__)
 
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

@application.route('/dynamic-kmean', methods = ['GET'])
def get_dynamic_data():
    return render_template('cluster-dynamic.html')

@application.route('/dynamic-kmean', methods = ['POST'])
def post_dynamic_data():
    numberOfClusters = request.form['Number Of Clusters']
    numberOfIterations = request.form['Number Of Iterations']
    att1 = request.form['Attribute 1']
    att2 = request.form['Attribute 2']
    att3 = request.form['Attribute 3']

    cursor=mysqlconnect.conn.cursor()
    # print("SELECT " + att1 + "," + att2 + "," + att3 + " FROM titanic") 
    cursor.execute("SELECT " + att1 + "," + att2 + "," + att3 + " FROM titanic")
    rows=cursor.fetchall() #fetches value
    centroids = []
    arrayAtt1 = []
    arrayAtt2 = []
    arrayAtt3 = []
    for row in rows:
        if row[0] == '':
            arrayAtt1.append(0)
        else:
            arrayAtt1.append(row[0])
        if row[1] == '':
            arrayAtt2.append(0)
        else:
            arrayAtt2.append(row[1])
        if row[2] == '':
            arrayAtt3.append(0)
        else:
            arrayAtt3.append(row[2])
    minX = arrayAtt1[0]
    maxX = arrayAtt1[0]
    minY = arrayAtt2[0]
    maxY = arrayAtt2[0]
    minZ = arrayAtt3[0]
    maxZ = arrayAtt3[0]
    for num in arrayAtt1:
        if(float(num) < float(minX)):
            minX = num
        if(float(num) > float(maxX)):
            maxX = num
    for num in arrayAtt2:
        if(float(num) < float(minY)):
            minY = num
        if(float(num) > float(maxY)):
            maxY = num
    for num in arrayAtt3:
        if(float(num) < float(minZ)):
            minZ = num
        if(float(num) > float(maxZ)):
            maxZ = num
    for i in range(int(numberOfClusters)):
        centroids.append([np.random.randint(math.floor(float(0)), math.floor(float(10000000))), np.random.randint(math.floor(float(0)), math.floor(float(10000000))), np.random.randint(math.floor(float(0)), math.floor(float(10000000)))])
    # print("done")
    # print(centroids)
    numberOfIterations = int(numberOfIterations) - 1
    objectOfClusterAndCentroids = iterateFun(centroids, rows, numberOfIterations)
    clusterOneSize = len(objectOfClusterAndCentroids["clusters"][1])
    distanceBetweenCentroids = []
    min = 100000
    max = 0
    minInd = 0
    maxInd = 0
    for i in range(len(objectOfClusterAndCentroids["clusters"])):
        if(len(objectOfClusterAndCentroids["clusters"][i]) < min):
            min = len(objectOfClusterAndCentroids["clusters"][i])
            minInd = i
        if(len(objectOfClusterAndCentroids["clusters"][i]) > max):
            max = len(objectOfClusterAndCentroids["clusters"][i])
            maxInd = i
    # print(objectOfClusterAndCentroids["centroids"][minInd])
    # print(objectOfClusterAndCentroids["centroids"][maxInd])
    minMaxClustDist = getDistance(objectOfClusterAndCentroids["centroids"][minInd],objectOfClusterAndCentroids["centroids"][maxInd][0], objectOfClusterAndCentroids["centroids"][maxInd][1], objectOfClusterAndCentroids["centroids"][maxInd][2])
    # print(objectOfClusterAndCentroids["centroids"][0])
    # print(objectOfClusterAndCentroids["centroids"][1])
    # cursor.execute("SELECT * FROM titanic where " + att1 + " = " + objectOfClusterAndCentroids["centroids"][minInd])
    oneTwoClustDist = getDistance(objectOfClusterAndCentroids["centroids"][0],objectOfClusterAndCentroids["centroids"][1][0], objectOfClusterAndCentroids["centroids"][1][1], objectOfClusterAndCentroids["centroids"][1][2])
    objectOfClusterAndCentroids["minMaxClustDist"] = minMaxClustDist    
    objectOfClusterAndCentroids["oneTwoClustDist"] = oneTwoClustDist    
    # print(minMaxClustDist)
    # print(oneTwoClustDist)
    html =  """<!DOCTYPE html>
    <html>
    <head>
    <title> Hello </title>
    </head>
    <body>
    <h1>SWETA NITINBHAI GADHIYA_1001720114</h1>
    Minimum - Maximum Centroid Distance:  """ + str(minMaxClustDist) + """<br> 1 - 2 Centroid Distance: """ 
    html = html + str(oneTwoClustDist) + "<br>"+ "All clusters centroids: " 
    html = html + str(objectOfClusterAndCentroids["centroids"]) + "<br>"
    for ind in range(len(objectOfClusterAndCentroids["clusters"])):
        html = html + "Centroid = " + str(objectOfClusterAndCentroids["centroids"][ind]) + ", Number of points = " + str(len(objectOfClusterAndCentroids["clusters"][ind])) + "<br>"
    html = html + "</body></html>"
    return html
    # return render_template('three-values.html', da = objectOfClusterAndCentroids["clusters"], dat = objectOfClusterAndCentroids["centroids"])
    # return str(clusterOneSize)

def iterateFun(centroids, rows, numberOfIterations):
    clusters = []
    for i in range(len(centroids)):
        clusters.append([])
    if(int(numberOfIterations) < 0):
        return {centroids: centroids, clusters: []}
    for row in rows:
        calculateDistance = []
        minDist = 100000
        for centroid in centroids:
            calculateDistance.append(getDistance(centroid, row[0] if row[0] != '' else 0 , row[1] if row[1] != '' else 0 , row[2] if row[2] != '' else 0 ))
        minClusterInd = 0
        for i in range(len(calculateDistance)):
            if(float(calculateDistance[i]) < float(minDist)): 
                minDist = float(calculateDistance[i])
                minClusterInd = int(i)
        clusters[minClusterInd].append([row[0] if row[0] != '' else 0 , row[1] if row[1] != '' else 0 , row[2] if row[2] != '' else 0 ])
        # for cl in clusters:
        #     print(len(cl))
    returnVar = {}
    returnVar["clusters"] = clusters
    returnVar["centroids"] = centroids 
    # print("done")
    if(numberOfIterations > 0):
        latestCentroid = []
        # print(len(clusters))
        for cluster in clusters:
            sumx = 0
            sumy = 0
            sumz = 0
            x = 0
            y = 0
            z = 0
            # print(len(cluster))
            for row in cluster:
                # print(row)
                sumx = sumx + float(row[0])
                sumy = sumy + float(row[1])
                sumz = sumz + float(row[2])
            if(len(cluster) != 0):
                x = sumx / len(cluster)
                y = sumy / len(cluster)
                z = sumz / len(cluster)
            latestCentroid.append([x, y, z])
            # print(latestCentroid)
        numberOfIterations = int(numberOfIterations) - 1    
        returnVar = iterateFun(latestCentroid, rows, numberOfIterations)
    return returnVar           

def getDistance(centroid, x, y, z):
    # print(centroid)
    # print(x)
    # print(y)
    # print(z)
    p1 = np.array([float(x), float(y), float(z)])
    p2 = np.array([float(centroid[0]), float(centroid[1]), float(centroid[2])])
    sqrd_dist = np.sum((p1-p2)**2, axis = 0)
    # print('s1')
    # print(sqrd_dist)
    # print('s2')
    distance = np.sqrt(sqrd_dist)
    return distance


@application.route('/with-iteration', methods=['GET'])
def cluster1_get():
    return render_template('cluster1-input.html')


@application.route('/with-iteration' , methods=['POST'])
def cluster1_post():
    cluster = request.form['cluster']
    iteration = request.form['iteration']

    cursor=mysqlconnect.conn.cursor()
    cursor.execute("SELECT * FROM titanic")
    rows=cursor.fetchall() #fetches value
    pclass = []
    boat = []
    survival = []
    age = []
    fare = []
    for row in rows:
        pclass.append(row[0])
        survival.append(row[1])
        if row[11] == '':
            boat.append(0)
        else:
            boat.append(row[11])
        if row[4] == '' or row[4]== None:
            age.append(0)
        else:
            age.append(row[4])
        if row[8] == '' or row[8]== None:
            fare.append(0)
        else:
            fare.append(row[8])
    #print(rows)
    x=random.uniform()
    y=random.uniform()



    # rows=cursor.fetchone()
    # print(rows)
    # row = []
    # count=0
    # while rows != False:
    #     x={}
    #     x['age'] = rows[4]
    #     x['fare'] = rows[8]
    #     row.append(x)
    #     #print(row)
    #     count=count+1
    #     rows=cursor.fetchone()
    #     print(rows)
    # print(count)
    return """sweta"""

@application.route('/without-iteration', methods=['GET'])
def cluster2_get():
    return render_template('cluster_without_iteration.html')

@application.route('/without-iteration', methods=['POST'])
def cluster2_post():
    return render_template('cluster1-output.html')





# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'



#add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text)) 


"""
# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'


 

 #add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL.
application.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))"""

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
