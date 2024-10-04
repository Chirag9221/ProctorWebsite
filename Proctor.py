@app.route('/proctor', methods=['POST'])
def proctor():
    if request.method == 'POST':
        duration_in_minutes = int(request.form.get('duration'))  # Get duration in minutes
        print('duration_in_mins:-',duration_in_minutes)
        duration_in_seconds = duration_in_minutes * 60  # Convert minutes to seconds
        microsoftForm = request.form.get('microsoftForm')
        print('Form link:', microsoftForm)
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--kiosk")  # Kiosk mode (Fullscreen)
        driver = webdriver.Chrome(options=options)

        # Open the Microsoft Form URL
        driver.get(microsoftForm)
        time.sleep(1)

        # Function to enter fullscreen mode using JavaScript
        def enter_fullscreen():
            driver.fullscreen_window()

        # Call the function to enter fullscreen initially
        enter_fullscreen()

        # Wait for the submit button to be clickable
        submit_button = WebDriverWait(driver, 180).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
        )

        # Function to unblock keys and close fullscreen after submission
        def end_test():
            print("Ending the test...")
            submit_button.click()  # Submit the form
            driver.execute_script('alert("Test duration ended. Submitting the form.");')
            time.sleep(1)
            driver.quit()  # Close the WebDriver
        
        # Function to suppress the Windows key press
        def block_windows_key(event):
            if event.name == 'windows':
                return False  # Suppress the key press

        # Block the ESC and ALT+TAB keys during the test
        keyboard.block_key('esc')
        # keyboard.block_key('esc')
        keyboard.block_key('alt')
        keyboard.block_key('tab')
        keyboard.block_key('f11')
        keyboard.block_key('fn')  # Note: fn key blocking may not work on all systems
        keyboard.block_key('delete')
        
        print(time.time)
        # Set a timer for the duration of the test (in seconds)
        test_timer = Timer(duration_in_seconds, end_test)
        test_timer.start()
        print(time.time)

        # Optional: Wait to observe the result after submission
        time.sleep(duration_in_seconds + 5)  # Adding a few seconds buffer to observe results
        
        # Close the WebDriver after submission if needed
        driver.quit()

        return jsonify({'success': True, 'message': 'Form has been submitted successfully.'})

    except Exception as e:
        print(f'An error occurred: {e}')
        return jsonify({'success': False, 'message': 'Error submitting form.'}), 500