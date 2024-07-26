from flask import Flask, render_template, redirect, request, json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Document:
    def __init__(self):
        self.submit_success = False
        self.enroll_success = False

    def calculate_age(self, dob):
        age = (int(dt.now().strftime('%Y')) - int(dob.strftime('%Y')))
        if (int(dt.now().strftime('%m')) < int(dob.strftime('%m'))): age = age - 1
        elif (int(dt.now().strftime('%m')) == int(dob.strftime('%m'))):
            if (int(dt.now().strftime('%d')) < int(dob.strftime('%d'))): age = age - 1
        return age

    def generate_rollno(self):
        count = len(list(Enrollment.query.all()))
        if count == 0: return 1
        lastroll = int(list(Enrollment.query.all())[-1].roll)
        return lastroll + 1

class LocationCities(db.Model):
    city = db.Column(db.String(50), primary_key = True)
    state = db.Column(db.String(50), nullable = False)
    country = db.Column(db.String(5), nullable = False)

class CompanyInfo(db.Model):
    infokey = db.Column(db.String(50), primary_key = True)
    infoval = db.Column(db.String(100), nullable = False)

class ManagingPeople(db.Model):
    empid = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(50), nullable = False)
    position = db.Column(db.String(20), nullable = False)
    dob = db.Column(db.Date, nullable = False)

class CourseList(db.Model):
    crsid = db.Column(db.String(10), primary_key = True)
    course = db.Column(db.String(80), nullable = False)
    duration = db.Column(db.Integer, nullable = False)
    amount = db.Column(db.Float, nullable = False)

class Enrollment(db.Model):
    roll = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(100), nullable = False)
    gender = db.Column(db.String(1), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    crsid = db.Column(db.String(10), db.ForeignKey(CourseList.crsid), nullable = False)
    city = db.Column(db.String(50), db.ForeignKey(LocationCities.city), nullable = False)
    doe = db.Column(db.Date, nullable = False)

with app.app_context(): db.create_all()
doc = Document()

@app.route('/')
def homepage():
    doc.enroll_success = False
    doc.submit_success = False
    hqcity = CompanyInfo.query.filter_by(infokey = 'HeadQuarter').first()
    headquart = LocationCities.query.filter_by(city = hqcity.infoval).first()
    return render_template(
        template_name_or_list = 'home.html',
        phone = CompanyInfo.query.filter_by(infokey = 'Phone').first().infoval,
        email = CompanyInfo.query.filter_by(infokey = 'Email').first().infoval,
        headquarter = [headquart.city, headquart.state, headquart.country]
    )

@app.route('/abouts')
def aboutpage():
    doc.enroll_success = False
    doc.submit_success = False
    founded = CompanyInfo.query.filter_by(infokey = 'FoundDate').first().infoval
    fndt = dt(
        year = int(founded.split('-')[0]),
        month = int(founded.split('-')[1]),
        day = int(founded.split('-')[2])
    )
    city = LocationCities.query.all()
    hqcity = CompanyInfo.query.filter_by(infokey = 'HeadQuarter').first()
    headquart = LocationCities.query.filter_by(city = hqcity.infoval).first()
    return render_template(
        template_name_or_list = 'about.html',
        city_list = ', '.join([i.city for i in list(city)]),
        headquarter = [headquart.city, headquart.state, headquart.country],
        found_date = fndt.strftime('%d') + ' ' + fndt.strftime('%B') + ' ' + fndt.strftime('%Y'),
        phone = CompanyInfo.query.filter_by(infokey = 'Phone').first().infoval,
        email = CompanyInfo.query.filter_by(infokey = 'Email').first().infoval,
        people = list(ManagingPeople.query.all()),
        agelist = {i.empid: doc.calculate_age(i.dob) for i in list(ManagingPeople.query.all())}
    )

@app.route('/courses')
def coursepage():
    hqcity = CompanyInfo.query.filter_by(infokey = 'HeadQuarter').first()
    headquart = LocationCities.query.filter_by(city = hqcity.infoval).first()
    amount_list = {i.crsid: '{:,}'.format(i.amount) for i in list(CourseList.query.all())}
    return render_template(
        template_name_or_list = 'courses.html',
        phone = CompanyInfo.query.filter_by(infokey = 'Phone').first().infoval,
        email = CompanyInfo.query.filter_by(infokey = 'Email').first().infoval,
        headquarter = [headquart.city, headquart.state, headquart.country],
        course_list = list(CourseList.query.all()),
        course_amt = amount_list,
        success = doc.enroll_success
    )

@app.route('/data', methods = ['GET','POST'])
def dataviewpage():
    doc.enroll_success = False
    doc.submit_success = False
    city_enroll = []

    hqcity = CompanyInfo.query.filter_by(infokey = 'HeadQuarter').first()
    headquart = LocationCities.query.filter_by(city = hqcity.infoval).first()
    course = list(CourseList.query.all())[0].crsid
    
    if request.method == 'POST':
        city_enroll = []
        course = request.form['course-id']

    city_list = [i.city for i in list(LocationCities.query.all())]
    for i in city_list:
        k = list(Enrollment.query.filter_by(crsid = course).filter_by(city = i).all())
        city_enroll.append(len(k))

    return render_template(
        template_name_or_list = 'stats.html',
        phone = CompanyInfo.query.filter_by(infokey = 'Phone').first().infoval,
        email = CompanyInfo.query.filter_by(infokey = 'Email').first().infoval,
        headquarter = [headquart.city, headquart.state, headquart.country],
        course_list = list(CourseList.query.all()),
        student_list = list(Enrollment.query.filter_by(crsid = course).all()),
        course_name = CourseList.query.filter_by(crsid = course).first().course,
        city_names = json.dumps(city_list),
        city_enroll = json.dumps(city_enroll)
    )

@app.route('/contact', methods=['GET','POST'])
def contactpage():
    doc.enroll_success = False
    doc.submit_success = False
    if request.method == 'POST':
        sender_name = request.form['sender-name']
        sender_phone = request.form['phone-code'] + '-' + request.form['phone-number']
        sender_message = request.form['sender-message']
        doc.submit_success = True
    
    return render_template(
        template_name_or_list = 'contact.html',
        day = dt.now().strftime('%d'),
        month = dt.now().strftime('%B'),
        year = dt.now().strftime('%Y'),
        weekday = dt.now().strftime('%A'),
        success = doc.submit_success
    )

@app.route('/enroll/<code>', methods = ['GET','POST'])
def enrollpage(code):
    doc.enroll_success = False
    doc.submit_success = False
    course_info = CourseList.query.filter_by(crsid = code).first()
    if request.method == 'POST':
        doc.enroll_success = True
        bd = request.form['birth-date'].split('-')
        student = Enrollment(
            roll = doc.generate_rollno(),
            fullname = request.form['enroll-name'],
            gender = request.form['enroll-gender'],
            dob = dt(year = int(bd[0]), month = int(bd[1]), day = int(bd[2])),
            crsid = code,
            city = request.form['branch-city'],
            doe = dt.now()
        )
        db.session.add(student)
        db.session.commit()
        return redirect('/courses')
    
    return render_template(
        template_name_or_list = 'enroll.html',
        course_code = code,
        course_name = course_info.course,
        day = dt.now().strftime('%d'),
        month = dt.now().strftime('%B'),
        year = dt.now().strftime('%Y'),
        weekday = dt.now().strftime('%A'),
        city_list = {i.city: (i.city + ', ' + i.state + ', ' + i.country) for i in list(LocationCities.query.all())},
        success = doc.enroll_success
    )

if __name__ == '__main__': app.run(debug = True)