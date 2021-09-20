import os
from datetime import datetime, timezone

import flask
from flask import request, abort, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
from pandas import DataFrame
from werkzeug.utils import secure_filename

import Code.MongoDB.MongoDb as MongoDB
from Code.AmbulanceAndEmergency import CSV_Parser

# import CSVStructrPopulation

UPLOAD_DIRECTORY = "../api_uploaded_files"
UPLOAD_SUMMARY_DIRECTORY = "../api_uploaded_files/Summary"
TEMPLATE_SUMMARY_DIRECTORY = "../Template"

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}
GROUP_BY_LABEL = [
    'Gender',
    'Position',
    'Sector',
    'Date',
]

GROUP_BY_DATASET = [
    'Gender',
    'Position',
]

TABLES = [
    'Collection_First2',
    'beneficiary',
    'trainers',
]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


app = flask.Flask(__name__)
CORS(app)

app.config["DEBUG"] = True
app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY
app.config['UPLOAD_SUMMARY_DIRECTORY'] = UPLOAD_SUMMARY_DIRECTORY
app.config['TEMPLATE_SUMMARY_DIRECTORY'] = TEMPLATE_SUMMARY_DIRECTORY


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


########################
# helper
########################
def get_absolute_path(fileName, isUploadSummary=False, isTemplateSummary=False):
    if isUploadSummary:
        return os.path.join(app.config['UPLOAD_SUMMARY_DIRECTORY'], fileName)
    elif (isTemplateSummary):
        return os.path.join(app.config['TEMPLATE_SUMMARY_DIRECTORY'], fileName)
    return os.path.join(app.config['UPLOAD_DIRECTORY'], fileName)


########################
# run
########################


"""
Get : Download relevant file 
Post :Upload relevant file
"""


@app.route("/api/v1/resources/files/<path:path>", methods=["GET", "POST"])
def get_file(path):
    if request.method == 'GET':
        """Download a file."""
        return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)

    if request.method == 'POST':
        """Upload a file."""
        # check if the post request has the file part
        if 'path' not in request.files:
            #        flash('No file part')
            #        return redirect(request.url)
            # Return 400 BAD REQUEST
            abort(400, "no subdirectories allowed")
        filesSaved = 0
        for file in request.files.getlist('path'):

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                saved_path = get_absolute_path(fileName=filename)
                print("normal", get_absolute_path(fileName="TotalVolunteerAndEmployee.xlsx"))
                print("template", get_absolute_path(fileName="TotalVolunteerAndEmployee.xlsx", isTemplateSummary=True))
                print(saved_path)

                file.save(saved_path)
                filesSaved += 1
                res = CSV_Parser.CSV_Parser(saved_path, summaryMode=False)
                # res.display() #todo display
                addDataFrameToDB(res.df1)
        if (filesSaved == len(request.files.getlist('path'))):
            return "", 201
        else:
            return "files saved {}".format(filesSaved), 206
    return "", 400


# if __name__ == '__main__':


DATABASE = "PSCR_First"
COLLECTION = "Collection_First2"

mongodb_client = PyMongo(app, MongoDB.DATABASE_URL)
db = mongodb_client.db
app.config["MONGO_URI"] = MongoDB.DATABASE_URL
mongodb_client = PyMongo(app)
db = mongodb_client.db
#
g_collection = db[COLLECTION]


def get_collection():
    global g_collection
    return g_collection


def setDataBase(db_name=DATABASE, collection=COLLECTION):
    global g_collection
    g_collection = db[collection]
    return g_collection


#
#
def addDataFrameToDB(df, addDate=False, offset=0):
    setDataBase()
    # file = r"C:\Users\predator\Desktop\PSCR\projects\Managments.xlsx"
    print("offset is : ", offset)

    # structure = CSVStructrPopulation.CSVStructurePopulation(fp, addDate, info=True, offset=offset)
    database_mongo = MongoDB.DataBase()
    database_mongo.addDF(db.Collection_First2, df)
    for row in db.Collection_First2.find({}, {"_id": 0, "index": 0}):
        print(row)


"""
Get : get data based on sheet and file
"""


@app.route("/api/v1/resources/database/show", methods=["GET"])
def showReport():
    global g_collection

    query_parameters = request.args
    startDate = query_parameters.get('dateFrom')
    endDate = query_parameters.get('dateTo')
    print("####", startDate, endDate)
    # print(g_collection.find_one(),startDate,endDate)
    # print(datetime(2021, 8, 28, 9, 55, 6, tzinfo=timezone.utc), type(datetime(2021, 8, 28, 9, 55, 6, tzinfo=timezone.utc)))

    filter_add_date = {
        '$set': {
            'date': {
                '$dateFromString': {
                    'dateString': '$date'
                }
            }
        }
    }
    filter_match = {
        '$match': {
            'date': {
                '$gt': datetime(2021, 8, 28, 9, 55, 6, tzinfo=timezone.utc)  # todo add date parameter

            }
            # 'date':{
            #     "$gte": {"$date": datetime.strptime('21-08-2021', '%d-%m-%Y').isoformat()},
            #     "$lt": {"$date": datetime.strptime('22-08-2021', '%d-%m-%Y').isoformat()},
            # }
        }
    }

    filter_json = {
        '$group': {
            '_id': {
                'category': '$category',
                'Gender': '$Gender',
                'file': '$file',
                'Position': '$Position',
                'date': '$date'
            },
            'count': {
                '$sum': '$Total'
            }
        }
    }

    filter_project = {
        '$project': {
            '_id': 0,
            'category': '$_id.category',
            'Gender': '$_id.Gender',
            'file': '$_id.file',
            'Position': '$_id.Position',
            'date': '$_id.date',
            'count': 1
        }
    }

    cursor = g_collection.aggregate([filter_add_date, filter_match, filter_json, filter_project])

    df = DataFrame(list(cursor))
    # print(tabulate(df, headers='keys', tablefmt='psql'))
    summary_create_path = get_absolute_path("S{}_E{}.xlsx".format(startDate, endDate), isUploadSummary=True)
    summary_template_path = get_absolute_path(fileName="TotalVolunteerAndEmployee.xlsx", isTemplateSummary=True)
    print(summary_create_path, summary_template_path)

    CSV_Parser.CSV_Parser(summary_template_path, summary_create_path=summary_create_path, summaryMode=True, df=df)

    return "", 201


app.run()

#
#
# def fetchFromDB(db_name=DATABASE, collection=COLLECTION):
#     collection = setDataBase(db_name, collection)
#     for row in collection.find({}, {"_id": 0, "index": 0}):
#         print(row)
#
#
#
#
#
# """
# Get all files in UPLOAD_DIRECTORY
# """
#
#
# @app.route("/api/v1/resources/files")
# def list_files():
#     """Endpoint to list files on the server."""
#     files = []
#     for filename in os.listdir(UPLOAD_DIRECTORY):
#         path = os.path.join(UPLOAD_DIRECTORY, filename)
#         if os.path.isfile(path):
#             files.append(filename)
#     return flask.jsonify(files)
#
#
# """
# Get : Download relevant file
# Post :Upload relevant file
# """
#
#
# @app.route("/api/v1/resources/files/<path:path>", methods=["GET", "POST"])
# def get_file(path):
#     if request.method == 'GET':
#         """Download a file."""
#         return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)
#
#     if request.method == 'POST':
#         """Upload a file."""
#         # check if the post request has the file part
#         if 'path' not in request.files:
#             #        flash('No file part')
#             #        return redirect(request.url)
#             # Return 400 BAD REQUEST
#             abort(400, "no subdirectories allowed")
#         file = request.files['path']
#         # if user does not select file, browser also
#         # submit an empty part without filename
#         # if file.filename == '':
#         #     flash('No selected file')
#         #     return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_DIRECTORY'], filename))
#     #            return redirect(url_for('uploaded_file',
#     #                                    filename=filename))
#
#     # Return 201 CREATED
#     return "", 201
#
#
# @app.route('/api/v1/resources/toDB/csv/upload/', methods=["POST"])
# def api_upload():
#     if request.method == 'POST':
#         """Upload a file."""
#         # check if the post request has the file part
#         if 'path' not in request.files:
#             abort(400, "no subdirectories allowed")
#         offset = 0
#         if 'offset' in request.args:
#             offset = eval(request.args['offset'])
#         file = request.files['path']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             if not (filename):
#                 return page_not_found(404)
#             file.save(os.path.join(app.config['UPLOAD_DIRECTORY'], filename))
#             fp = """{}/{file}""".format(UPLOAD_DIRECTORY, file=filename)
#             convertCSV2DB(fp, addDate=True, offset=offset)
#             # Return 201 CREATED
#             return "", 201
#         return page_not_found(405)
#
#
# @app.route('/api/v1/resources/toDB/csv/upload/', methods=["GET"])
# def api_getAll():
#     if request.method == 'GET':
#         """Get Table Content"""
#         fetchFromDB()
#         return "", 200
#     return page_not_found(405)
#
#
# ########## Chart Helper ###############
#
# def getDBLabels(collection, is_filter=False):
#     label_s = set()
#     if is_filter == False:
#         for row in collection.find({}, {"_id": 0, "index": 0}):
#             label_s.add(row['Sector'])
#         return list(label_s)
#
#
# def getDBDataSet(collection, column=None):
#     dataset_s = set()
#     if column:
#         for row in collection.find({}, {"_id": 0, "index": 0}):
#             print("-------216:", row)
#             if column in row:
#                 dataset_s.add(row[column])
#         return list(dataset_s)
#     print(collection)
#     for row in collection.find({}, {"_id": 0, "index": 0}):
#         return list(row.keys())
#
#
# ########## Chart API ###############
#
# # @app.route("/api/v1/resources/chart/GetLabels")
# # def get_labels():
# #     return flask.jsonify(result=getDBLabels(get_collection()))
#
# @app.route("/api/v1/resources/chart/GetGroupByLabel")
# def get_group_by_labels():
#     return flask.jsonify(GROUP_BY_LABEL)
#
#
# @app.route("/api/v1/resources/chart/GetGroupByDataSet")
# def get_group_by_dataset():
#     return flask.jsonify(GROUP_BY_DATASET)
#
#
# @app.route("/api/v1/resources/chart/GetDataSet")
# def get_dataset():
#     query_parameters = request.args
#     showFromTablesOnly = query_parameters.get('tables')
#     onlyTables_l = TABLES
#     print("tables param : ",showFromTablesOnly)
#     if showFromTablesOnly:
#         if showFromTablesOnly.startswith('[') and showFromTablesOnly.endswith(']'):
#             onlyTables_l = []
#             for table in showFromTablesOnly[1:-1].split(','):
#                 print("adding: ",table.strip())
#                 onlyTables_l.append(table.strip())
#     print(onlyTables_l)
#     showValuesOnly = query_parameters.get('values')
#     if (showValuesOnly == "True"):
#         res = set()
#         for collection in onlyTables_l:
#             res.update(getDBDataSet(db[collection]))
#         return flask.jsonify(result=list(res))
#     column = query_parameters.get('column')
#     original_collection = get_collection()
#     res = dict()
#     for collection in onlyTables_l:
#         res[collection] = getDBDataSet(db[collection], column)
#     setDataBase(original_collection)
#     return flask.jsonify(result=res)
#
#
# def group_by(label="Sector", dataSet="Position", filterBy=dict(), countBy="Total"):
#     global g_collection
#     print(g_collection.find_one())
#     filter_json = {
#         "$group":
#             {"_id": {
#                 label: "$" + label,
#                 dataSet: "$" + dataSet
#             },
#                 "count": {"$sum": "$" + countBy}},
#
#         #     {
#         # "$sort": { "Date" : -1 }
#         # }
#     }
#     if filterBy:
#         for key in filterBy:
#             filter_json["$group"]["_id"][key] = "$" + filterBy[key]
#             find_json = {}
#     print("filterBy", filter_json)
#     cursor = g_collection.aggregate([
#         {"$match": {"Gender": "male"}}, filter_json])
#     json_data = dumps(list(cursor))
#     print("data:", json_data)
#     return json_data
#
#
# @app.route("/api/v1/resources/chart/groupBy")
# def get_group_by():
#     query_parameters = request.args
#     label = query_parameters.get('label')
#     dataSet = query_parameters.get('dataSet')
#     filter = query_parameters.get('filter')
#     if dataSet and dataSet.startswith('[') and dataSet.endswith(']'):
#         dataSet = dataSet[1:-1].split(',')
#     if filter:
#         if filter.startswith('{') and filter.endswith('}'):
#             filter = json.loads(filter)
#
#     return group_by(label=label, dataSet=dataSet, filterBy=filter, countBy="Total")
#
#
# @app.route("/add_one")
# def add_one():
#     db.TestDB.insert_one({'title': "todo title", 'body': "todo body"})
#     return flask.jsonify(message="success")
#
#
# @app.route("/add_many")
# def add_many():
#     offset = 0
#     uploadTime = (datetime(2021, 7, 15, 12, 13, 43) + timedelta(days=offset)).replace(microsecond=0).isoformat()
#     db.beneficiary.insert_many([
#         {'_id': 1,
#          'Sector': "Ambulance officers",
#          'Position': "staff",
#          'Gender': "male",
#          'Rank': "Administrative",
#          'Date': uploadTime,
#          'Total': 2500},
#         {'_id': 2,
#          'Sector': "Ambulance officers",
#          'Position': "staff",
#          'Gender': "male",
#          'Rank': "Technical",
#          'Date': uploadTime,
#          'Total': 2500},
#
#         {'_id': 3,
#          'Sector': "Ambulance officers",
#          'Position': "staff",
#          'Gender': "female",
#          'Rank': "Administrative",
#          'Date': uploadTime,
#          'Total': 7500},
#         {'_id': 4,
#          'Sector': "Ambulance officers",
#          'Position': "staff",
#          'Gender': "female",
#          'Rank': "Technical",
#          'Date': uploadTime,
#          'Total': 2500},
#         ###########Rehabilitation#########################
#         {'_id': 5,
#          'Sector': "Rehabilitation",
#          'Position': "staff",
#          'Gender': "male",
#          'Rank': "Administrative",
#          'Date': uploadTime,
#          'Total': 3000},
#         {'_id': 6,
#          'Sector': "Rehabilitation",
#          'Position': "staff",
#          'Gender': "male",
#          'Rank': "Technical",
#          'Date': uploadTime,
#          'Total': 3000},
#
#         {'_id': 7,
#          'Sector': "Rehabilitation",
#          'Position': "staff",
#          'Gender': "female",
#          'Rank': "Administrative",
#          'Date': uploadTime,
#          'Total': 3000},
#         {'_id': 8,
#          'Sector': "Rehabilitation",
#          'Position': "staff",
#          'Gender': "female",
#          'Rank': "Technical",
#          'Date': uploadTime,
#          'Total': 3000},
#         ####################################
#
#     ])
#
#     db.trainers.insert_many([
#         {'_id': 1,
#          'Sector': "Ambulance officers",
#          'Position': "staff",
#          'Total_Couch': 2500},
#         {'_id': 2,
#          'Sector': "Rehabilitation",
#          'Position': "staff",
#          'Total_Couch': 3000},
#
#         ####################################
#
#     ])
#     return flask.jsonify(message="success")
#
#
# @app.route("/")
# def home():
#     todos = db.Collection_first.find()
#     for todo in todos:
#         print(todo)
#         return flask.jsonify([5])
#     return flask.jsonify([todo for todo in todos])
#
#
# @app.route("/get_todo/<int:todoId>")
# def insert_one(todoId):
#     todo = db.todos.find_one({"_id": todoId})
#     return todo
#
#
