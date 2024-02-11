from collections import OrderedDict
from studentvue import StudentVue
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from path import *

def use_regex(input_text):
    return re.findall(r'(.sID":\d+)', input_text)

username = ''
password = ''
domain_url = ""

login_url = " https://parentvue.cobbk12.org/./PXP2_Login_Student.aspx?regenerateSessionId=True"
gradebook_url = "https://parentvue.cobbk12.org/PXP2_Gradebook.aspx"

r = requests.Session()

#print([type(item) for item in list(soup.children)])
# html = list(soup.children)[3]       #html tag and its children: 4th item in list
# print(list(html.children))

# constructor

def login(user, pswd, url):
    login = r.get(url)
    soup = BeautifulSoup(login.content, "html.parser")

    viewstate = soup.find('input', {"id": "__VIEWSTATE"}).get('value')
    viewstategen = soup.find('input', {"id": "__VIEWSTATEGENERATOR"}).get('value')
    eventvalid = soup.find('input', {"id": "__EVENTVALIDATION"}).get('value')
    # print(soup.find('p'))

    # create post request payload/login
    login_data = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategen,
        "__EVENTVALIDATION": eventvalid,
        "ctl00$MainContent$username": user,
        "ctl00$MainContent$password": pswd,
        "ctl00$MainContent$Submit1": "Login",
    }

    print("Attemping login...")
    result = str(r.post(url, data=login_data))
    print(result)

    if result == "<Response [200]>":
        print("Logged in")
    else:
        print("Site Error " + result)

    return StudentVue(username, password, domain_url)

def get_gradebook():
    grades = r.get(gradebook_url)
    soup = BeautifulSoup(grades.content, "html.parser")

    school = soup.find(id="ctl00_ctl00_MainContent_PXPMainContent_repSchoolClasses_ctl00_ctl00_SchoolClassesPanel")
    schoolName = str(school.find(class_="title").get_text())
    print(schoolName + "\n")

    classes = soup.find(id="gb-classes")
    classNames = classes.find_all(class_="btn btn-link course-title")
    teachers = classes.find_all(class_="teacher hide-for-screen")
    classGrades = classes.find_all(class_="score")
    classList = classes.find_all(class_="row gb-class-header gb-class-row flexbox horizontal")
    filteredClassGrades = []
    # print(len(classGrades))
    # print(classGrades)
    # print(len(filteredClassGrades))
    #print(classList)


    for i in range(len(classGrades)):
        if str(classGrades[i].get_text())[-1] == '%' and str(classGrades[i].get_text())[0:3] != '0.0':
            filteredClassGrades.append(str(classGrades[i].get_text()))
    # print(filteredClassGrades)
    classPeriod = []
    className = []
    classString = []
    classGrade = []
    for i in range(len(classList)):
        classPeriod.append(str(classNames[i].get_text())[0])
        className.append(str(classNames[i].get_text())[3:])
        classString.append(str(teachers[i].get_text()))
        classGrade.append(filteredClassGrades[i])

    global periods
    periods = len(filteredClassGrades)

    student = pd.DataFrame({
        "Period": classPeriod,
        "Class": className,
        "Teacher": classString,
        "Grade": classGrade,
    })
    return student.to_string(index=False)
# class ID
def get_classID():
    grades = r.get(gradebook_url)
    soup = BeautifulSoup(grades.content, "html.parser")

    classes = soup.find(id="gb-classes")
    classList = classes.find_all(class_="row gb-class-header gb-class-row flexbox horizontal")
    classIDs = use_regex(str(classList))
    #print(classIDs)
    classIDList = []
    for item in classIDs:
        classIDList.append(item[6:])
    return classIDList
# assignments
def listRecursive (d, key):
    for k, v in d.items ():
        if isinstance (v, OrderedDict):
            for found in listRecursive (v, key):
                yield found
        if k == key:
            yield v
def findnth(string, substring):
   return string.find(substring, string.find(substring)+1)

def get_assignments(sv, classID):
    # gradebook: OrderedDict = sv.get_gradebook()
    # #courses: list = gradebook.get('Gradebook').get('Courses').get('Course')
    # courses: list = gradebook['Gradebook']['Courses']['Course']

    # period = int(input("Which period's gradebook do you want to view? "))

    # try:
    #     course = courses[period - 1]
    # except:
    #     print("Error, Period is not available")
    #     return 1

    # # Print General Info
    # #print(course)
    # name = course.get('@Title')
    # overall_grade = 0

    # overall_grade_list = course.get('Mark')
    # print(overall_grade_list)
    # #overall_grade: OrderedDict = overall_grade.get('@CalculatedScoreRaw')
    # for found in listRecursive(course, '@CalculatedScoreRaw'):
    #     overall_grade = found
    # print(f"{name}\nOverall Grade: {overall_grade}")

    # Return List of Assignments
    grades = r.get(gradebook_url)
    soup = BeautifulSoup(grades.content, "html.parser")

    #toNavigate = soup.find_all("a",{"class":"list-group-item"})[7]["href"]
    #print(toNavigate)
       
    userdata = json.loads(str(soup.find("button",{"class":"btn btn-link course-title"})["data-focus"])) 
    #C69FDB1D-4F23-4757-83E3-6B828E9C8EB5
    idNumber = userdata["FocusArgs"]["studentGU"]
    courseID = userdata["FocusArgs"]["studentGU"]
    schoolNumber = userdata["FocusArgs"]["schoolID"]
    gradePeriodGU = userdata["FocusArgs"]["gradePeriodGU"]
    OrgYearGU = userdata["FocusArgs"]["OrgYearGU"]
    school = soup.find("div",{"class":"school"}).get_text()

    session = r.get("https://parentvue.cobbk12.org/PXP2_Gradebook.aspx?AGU=0&studentGU={}".format(courseID))

    data ={"request":{"control":"Gradebook_ClassDetails","parameters":{"schoolID":int(schoolNumber),"classID":int(classID),"gradePeriodGU":gradePeriodGU, "subjectID":-1,"teacherID":-1,"assignmentID":-1,"studentGU":idNumber,"AGU":"0","OrgYearGU":OrgYearGU}}}
    session = r.post("https://parentvue.cobbk12.org/service/PXP2Communication.asmx/LoadControl",json=data)
    class_information = session.json()['d']['Data']['html']
    occurrence = findnth(class_information, '"dataSource"')
    #start = class_information.index('"dataSource"')
    #print(occurrence)
    start = occurrence
    #print(class_information[start:])
    end = class_information[start:].index("}))")
    assignment_data = json.loads("{" + class_information[start: start + end] + "}")

    assignments = json.loads(json.dumps(assignment_data, sort_keys=True, indent=4))
    #print(assignment_data)
    assignment_num = str(assignments).count("GBAssignmentType")
    print("Assignments: " + str(assignment_num))

    dataSource = (assignments['dataSource'])

    assignment_name_arr = []
    assignment_type_arr = []
    assignment_score_arr = []

    for i in range(assignment_num):
        assignment_name_arr.append(json.loads(dataSource[i]['GBAssignment'])['value'])
        assignment_type_arr.append(dataSource[i]['GBAssignmentType'])
        assignment_score_arr.append(json.loads(dataSource[i]['GBScore'])['value'])

    assignmentDF = pd.DataFrame({
        "Assignment": assignment_name_arr,
        "Assignment Type": assignment_type_arr,
        "Score": assignment_score_arr
    })
    return assignmentDF


# categories/avgs
def get_categories(classID):
    grades = r.get(gradebook_url)
    soup = BeautifulSoup(grades.content, "html.parser")

    #toNavigate = soup.find_all("a",{"class":"list-group-item"})[7]["href"]
    #print(toNavigate)
       
    userdata = json.loads(str(soup.find("button",{"class":"btn btn-link course-title"})["data-focus"])) 
    #C69FDB1D-4F23-4757-83E3-6B828E9C8EB5
    idNumber = userdata["FocusArgs"]["studentGU"]
    courseID = userdata["FocusArgs"]["studentGU"]
    schoolNumber = userdata["FocusArgs"]["schoolID"]
    gradePeriodGU = userdata["FocusArgs"]["gradePeriodGU"]
    OrgYearGU = userdata["FocusArgs"]["OrgYearGU"]
    school = soup.find("div",{"class":"school"}).get_text()

    session = r.get("https://parentvue.cobbk12.org/PXP2_Gradebook.aspx?AGU=0&studentGU={}".format(courseID))

    data ={"request":{"control":"Gradebook_ClassDetails","parameters":{"schoolID":int(schoolNumber),"classID":int(classID),"gradePeriodGU":gradePeriodGU, "subjectID":-1,"teacherID":-1,"assignmentID":-1,"studentGU":idNumber,"AGU":"0","OrgYearGU":OrgYearGU}}}
    session = r.post("https://parentvue.cobbk12.org/service/PXP2Communication.asmx/LoadControl",json=data)
    class_information = session.json()['d']['Data']['html']
    start = class_information.index('"dataSource"')
    end = class_information[start:].index("}]")
    assignment_data = json.loads("{" + class_information[start: start + end] + "}]}")

    assignments = json.loads(json.dumps(assignment_data, sort_keys=True, indent=4))
    categories = str(assignments).count("GBAssignmentType")
    #print("Categories: " + str(categories))

    dataSource = (assignments['dataSource'])
    #print(dataSource)

    categoryArr = []
    weightArr = []
    avgArr = []

    for i in range(categories):
        categoryArr.append((dataSource[i])['GBAssignmentType'])
        weightArr.append((dataSource[i])['GBWeight'])
        try:
            avgArr.append(round(float((dataSource[i])['GBPoints']) / float((dataSource[i])['GBPointsPossible']) * 100.0, 2))
        except:
            avgArr.append(0)
    avgArr.pop()
    avgArr.append(str((dataSource[categories - 1])['GBCurrentScore'])[:-1])



    categoryDF = pd.DataFrame({
        "Category": categoryArr,
        "Weight": weightArr,
        "Average": avgArr
    })
    return categoryDF

def get_info(sv, period):
    gradebook: OrderedDict = sv.get_gradebook()
    #courses: list = gradebook.get('Gradebook').get('Courses').get('Course')
    courses: list = gradebook['Gradebook']['Courses']['Course']

    try:
        course = courses[period - 1]
    except:
        print("Error, Period is not available")
        return 1

    # Print General Info
    #print(course)
    name = course.get('@Title')
    return f"{name}"

def handle_csv(dataframe, name):
    print(get_download_folder())
    filename = name.replace('/', " ")
    dataframe.to_csv(get_download_folder() + '\\' + filename + '.csv', index = False)
    return ("File saved to Downloads folder")
#get_gradebook()
#print(get_gradebook())
#login(username, password, login_url)

#print(get_classID())

# final grade
#print(get_classID()[0])
#print(get_classID()[1])
