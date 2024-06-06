from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from datetime import datetime
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
# Retrieve the MongoDB URI from environment variables
uri = os.getenv("mongo_srv")

client = MongoClient(uri)
db = client['instrumentos']
students_collection = db['estudiantes']
instruments_collection = db['instrumentos']
teachers_collection = db['profesores']
prestamos_collection = db['prestamosEventuales']

def format_dates(result):
    for key, value in result.items():
        if isinstance(value, dict):
            format_dates(value)
        elif isinstance(value, list):
            for item in value:
                format_dates(item)
        elif key.endswith('fechaOficializacion') or key.endswith('fechaSolicitud'):
            if isinstance(value, dict) and '$date' in value:
                result[key] = datetime.strptime(value['$date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
            elif isinstance(value, datetime):
                result[key] = value.strftime('%Y-%m-%d')
    return result

@app.route("/", methods=('GET', 'POST'))
def index():
    query_result = None
    error = None
    if request.method == 'POST':
        query_str = request.form['query']
        try:
            query = json.loads(query_str)
            query_result = list(students_collection.find(query))
            query_result = [format_dates(result) for result in query_result]
        except Exception as e:
            error = str(e)
    
    return render_template('index.html', query_result=query_result, error=error)

@app.route("/students", methods=('GET', 'POST'))
def view_students():
    if request.method == 'POST':
        query_rut = request.form['query']
        # Assuming 'rut' is the key in your MongoDB documents
        query_result = students_collection.find({"rut": query_rut})
        # Process the query result as needed
        return render_template('students.html', students=query_result)
    else:
        all_students = list(students_collection.find())
        return render_template('students.html', students=all_students)

@app.route("/instruments", methods=('GET', 'POST'))
def view_instruments():
    all_instruments = list(instruments_collection.find())
    return render_template('instruments.html', instruments=all_instruments)

@app.route("/teachers", methods=('GET', 'POST'))
def view_teachers():
    all_teachers = list(teachers_collection.find())
    return render_template('teachers.html', teachers=all_teachers)

@app.route("/prestamosEventuales", methods=['GET'])
def view_prestamos():
    all_prestamos = list(prestamos_collection.find())
    all_prestamos = [format_dates(prestamo) for prestamo in all_prestamos]
    return render_template('prestamos.html', prestamos=all_prestamos)

@app.post("/<id>/delete/")
def delete(id):
    students_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))

@app.post("/instruments/<id>/delete/")
def delete_instrument(id):
    instruments_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('view_instruments'))

@app.route("/students/<id>/delete/", methods=['POST'])
def delete_student(id):
    students_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('view_students'))


if __name__ == "__main__":
    app.run(debug=True)



