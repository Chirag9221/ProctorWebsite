from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for sessions

# Global variable to store test settings
test_settings = {
    'form_link': 'https://forms.office.com/e/PviVjEaFp4',
    'test_name': 'Sample Test',
    'duration': '30 minutes'
}

# @app.route('/')
# def home():
#     return render_template('index.html', **test_settings)


@app.route('/starttest', methods=['GET', 'POST'])
def home():
    # Initialize variables to hold data
    row0 = row1 = row2 = None
    rowlist = []
    # Check if the request method is POST
    if request.method == 'POST':
        row0 = request.form.get('row1')
        row1 = request.form.get('row2')
        row2 = request.form.get('row3')
        rowlist=[row0,row1,row2]

    # Example data to pass to the template
    test_settings = {
        'row0': row0,
        'row1': row1,
        'row2': row2,
        'form_link': 'https://forms.office.com/e/PviVjEaFp4'
    }
    if len(rowlist) == 0:
        return render_template('index.html', **test_settings)
    else:
        print(rowlist)
        return render_template('index.html',rowlist=rowlist)

@app.route('/adminForm', methods=['GET', 'POST'])
def adminForm():
    if request.method == 'POST':
        global test_settings
        test_settings['form_link'] = request.form.get('formLink')
        test_settings['test_name'] = request.form.get('testName')
        duration = request.form.get('duration')
        minutes = int(float(duration) * 60)
        test_settings['duration'] = f"{minutes // 60} hours {minutes % 60} minutes"
        return render_template('test.html')
    return render_template('adminForm.html')


@app.route('/', methods=['GET', 'POST'])
def sgid_form():
    if request.method == 'POST':
        sgid = request.form['sgid']
        print('form data:', sgid)
        
        # Connect to the database
        database_connection = sqlite3.connect('HR.db')
        database_cursor = database_connection.cursor()
        
        # Check if the SGID exists
        data = database_cursor.execute("SELECT sgid FROM hrData WHERE sgid = ?", (sgid,))
        sgid = data.fetchone()
        
        if sgid is not None:
            print(sgid[0])
            # Fetch relevant data based on the SGID
            database_cursor.execute("SELECT * FROM Admin_Assessment_Setup WHERE sgid = ?", (sgid[0],))
            rows = database_cursor.fetchall()
            print(rows)
            database_connection.close()

            # store the segid in session 
            session['sgid'] = sgid[0]
            
            # Store rows in session
            session['rows'] = rows
            
            # Redirect to /test route
            return redirect(url_for('dashboard'))
        
        else:
            # If SGID is invalid, reload the form with a warning message
            return render_template('AdminLogin.html', warningdata='Please enter a valid SGID')
    
    return render_template('AdminLogin.html')

@app.route('/dashboard')
def dashboard():
    # Get the sgid data from session
    sgid = session.get('sgid',None)

    # Connect to the database
    database_connection = sqlite3.connect('HR.db')
    database_cursor = database_connection.cursor()
    
    # Check if the SGID exists
    data = database_cursor.execute("SELECT * FROM Admin_Assessment_Setup WHERE sgid = ?", (sgid,))
    assesment_data = data.fetchall()

    # data = database_cursor.execute("DELETE * FROM Admin_Assessment_Setup")

    database_connection.close()
    print(assesment_data)

    return render_template('dashboard.html',rows=assesment_data)

# @app.route('/deletecard',methods=['POST','GET'])
# def deletecard():
#     if request.method == 'post':
#         id = request.form['id']
#         sgid = request.form['sgid']
        


@app.route('/submission-success')
def submission_success():
    return render_template('thankyou.html')


@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/card-details', methods=['POST'])
def card_details():
    row0 = request.form.get('row1')
    row1 = request.form.get('row2')
    row2 = request.form.get('row3')
    print(f"Row0: {row0}, Row1: {row1}, Row2: {row2}")
    # Process the data and render a template or perform any action
    return f"Details - Row0: {row0}, Row1: {row1}, Row2: {row2}"


@app.route('/logout')
def logout():
    return 

if __name__ == '__main__':
    app.run(debug=True)

