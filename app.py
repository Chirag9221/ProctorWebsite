from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from flask import jsonify
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.window import WindowTypes
import keyboard
from threading import Timer


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
        id = request.form.get('id')
        sgid = request.form.get('sgid')
        assessment_name = request.form.get('assessment_name')
        microsoftForm = request.form.get('microsoftForm')
        duration = request.form.get('duration')

        rowlist=[id,sgid,assessment_name,microsoftForm,duration]
        print(rowlist)

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

@app.route('/proctor', methods=['POST'])
def proctor():
    if request.method == 'POST':
        duration = int(request.form.get('duration')) * 60  # Convert duration to seconds
        microsoftForm = request.form.get('microsoftForm')
        print('Form link:', microsoftForm)
        
    try:
        # Initialize WebDriver with Chrome options for Kiosk Mode
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--kiosk")  # Open Chrome in Kiosk Mode
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Open the Microsoft Form URL in Kiosk Mode
        driver.get(microsoftForm)
        time.sleep(3)  # Allow the page to load
        
        # Count of Escape key presses (if needed)
        count_of_Esc = 0
        
        # Function to submit the form and exit fullscreen after duration ends
        def end_test():
            try:
                submit_button = WebDriverWait(driver, 180).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
                )
                submit_button.click()
                print("Form submitted.")
            except Exception as e:
                print(f"An error occurred while submitting: {e}")
            finally:
                driver.quit()  # Close the browser after submission
        
        # Set the timer to end the test after the specified duration
        test_timer = Timer(duration, end_test)
        test_timer.start()  # Start the timer
        
        # Monitor form submission or other activities
        submit_button = WebDriverWait(driver, 180).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
        )
        
        # After the form is submitted manually, exit fullscreen and close the browser
        submit_button.click()
        driver.quit()  # Close the browser after manual submission

        return jsonify({'success': True, 'message': 'Form has been submitted successfully.'})

    except Exception as e:
        print(f'An error occurred: {e}')
        return jsonify({'success': False, 'message': 'Error submitting form.'}), 500



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

