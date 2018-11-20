from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import datetime
import sys, getopt
import threading
import os

def periodically_check_wam(result_filename, username, password, course_title, email_account, email_password,
                           time_frequency=600):
    check_wam(
        result_filename=result_filename,
        username=username,
        password=password,
        course_title=course_title,
        email_account=email_account,
        email_password=email_password
    )
    print("------------------------------------------")

    threading.Timer(int(time_frequency), periodically_check_wam,
                    args=[result_filename, username, password, course_title, email_account, email_password,
                          time_frequency]).start()


def send_notification(result, email_account, email_password):
    import smtplib
    print("(Sending notification email...)")

    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(email_account, email_password)

        header = 'From: %s\n' % email_account
        header += 'To: %s\n' % email_account
        header += 'Subject: %s\n\n' % 'Your WAM has changed'
        message = header + result

        server.sendmail(email_account, email_account, message)
        server.quit()
        print("(Notification email sent!)")
    except Exception as err:
        print("(Failed sending Notification email: %s)" % str(err))


def check_wam(result_filename, username, password, course_title, email_account, email_password):
    print("(Logging in...)")

    if os.path.exists(result_filename):
        with open(result_filename, 'r') as f:
            lines = f.readlines()

            if len(lines) == 0:
                prev_result_text = ""
            else:
                prev_result_text = lines[0]
    else:
        prev_result_text = ""

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(
        "https://prod.ss.unimelb.edu.au/student/SM/ResultsDtls10.aspx?r=%23UM.STUDENT.APPLICANT&f=$S1.EST.RSLTDTLS.WEB")

    assert "Log In" in driver.title

    username_element = driver.find_element_by_id("ctl00_Content_txtUserName_txtText")
    password_element = driver.find_element_by_id("ctl00_Content_txtPassword_txtText")

    username_element.send_keys(username)
    password_element.send_keys(password)

    driver.find_element_by_name("ctl00$Content$cmdLogin").click()

    try:
        print("(Getting your result...)")

        next_link = driver.find_element_by_xpath('//*[contains(text(), "' + course_title + '")]/ancestor::tr[1]//a[1]')

        next_link.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'UMWAMText')))
        result_element = driver.find_element(By.CLASS_NAME, 'UMWAMText')
        result_text = result_element.text

        print(result_text)
        print("(As at " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + ")")

        with open(result_filename, 'w+') as f:
            f.write(result_text)

            if prev_result_text == result_text:
                print("(No WAM change detected)")
            elif prev_result_text == '':
                print("(First time running the script)")
            else:
                print("(WAM changed!)")
                send_notification(result_text, email_account, email_password)

    except TimeoutException:
        print("error loading result page")
    except Exception as err:
        print("Unexpected error: " + str(err))


def main(argv):
    try:
        opts, args = getopt.getopt(argv, ":h:u:p:c:g:P:f:",
                                   [
                                       "username=",
                                       "password=",
                                       "course=",
                                       "gmail=",
                                       "gmailpassword=",
                                       "frequency="
                                   ])
    except getopt.GetoptError:
        print('incorrect arguments')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-u <unimelb_username> -o <unimelb_password> -c <course_short_title> -g <gmail_account> -p '
                  '<gmail_password> -f <time_frequency(seconds)>')
            sys.exit()
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-c", "--course"):
            course_title = arg
        elif opt in ("-g", "--gmail"):
            email_account = arg
        elif opt in ("-P", "--gmailpassword"):
            email_password = arg
        elif opt in ("-f", "--frequency"):
            time_frequency = arg

    result_filename = "result_text_%s.html" % username
    periodically_check_wam(result_filename, username, password, course_title, email_account, email_password,
                           time_frequency)


if __name__ == "__main__":
    main(sys.argv[1:])
