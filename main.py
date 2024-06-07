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
    return render_template('index.html')

@app.route("/students", methods=('GET', 'POST'))
def view_students():
    if request.method == 'POST':
        query_str = request.form.get('query')
        if query_str:
            query = {"rut": query_str}
            query_result = list(students_collection.find(query))
            query_result = [format_dates(result) for result in query_result]
            return render_template('students.html', students=query_result)
        else:
            return render_template('students.html', students=[])
    else:
        all_students = list(students_collection.find())
        return render_template('students.html', students=all_students)

# @app.route("/instruments", methods=('GET', 'POST'))
# def view_instruments():
#     all_instruments = list(instruments_collection.find())
#     return render_template('instruments.html', instruments=all_instruments)

@app.route("/instruments", methods=('GET', 'POST'))
def view_instruments():
    if request.method == 'POST':
        instrument_name = request.form.get('instrument_name')
        if instrument_name:
            instruments = list(instruments_collection.find({"nombre": instrument_name}))
        else:
            instruments = list(instruments_collection.find())
    else:
        instruments = list(instruments_collection.find())
    return render_template('instruments.html', instruments=instruments)

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
    return redirect(url_for('view_students'))

@app.post("/instruments/<id>/delete/")
def delete_instrument(id):
    instruments_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('view_instruments'))

@app.route("/students/<id>/delete/", methods=['POST'])
def delete_student(id):
    students_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('view_students'))


    
@app.route("/add_student", methods=['GET', 'POST'])
def view_student():
    if request.method == 'POST':
        # Process the form submission and add the new student to the database
        # This logic will depend on how you handle form submissions in your Flask app
        return redirect(url_for('index'))  # Redirect back to the index page after adding the student
    else:
        return render_template('add_students.html')


@app.route("/submit_student", methods=['POST'])
def submit_student():
    if request.method == 'POST':
        # Get the form data
        rut = request.form['rut']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        carrera = request.form['carrera']
        certificadoAr = request.form['certificadoAr']
        email = request.form['email']
        nombreDePila = request.form['nombreDePila']
        telefono = request.form['telefono']
        
        # Insert the student data into the collection
        new_student = {
            "rut": rut,
            "apellido1": apellido1,
            "apellido2": apellido2,
            "carrera": carrera,
            "certificadoAr": certificadoAr,
            "email": email,
            "nombreDePila": nombreDePila,
            "telefono": telefono
        }
        students_collection.insert_one(new_student)
        
        # Redirect to the view_students route or wherever you want to redirect after adding the student
        return redirect(url_for('view_students'))
    
    

if __name__ == "__main__":
    app.run(debug=True)
