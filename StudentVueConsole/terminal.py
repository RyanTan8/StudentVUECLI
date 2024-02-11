from studentvuerequests import *
import os
import time


running = True
global sv
def login_page():
    print("StudentVue - Terminal \n©Copyright 2022 Edupoint, LLC")
    print("""------------------------------------\n
    Login - Cobb County School District\n
    ------------------------------------\n""")
    username = input("Username: ")
    password = input("Password: ")
    return login(username, password, login_url)
sv = login_page()

def main_page():

    os.system('cls')

    home = """\nSelect an option:\n
            [1] View gradebook\n
            [2] View course assignments\n
            [3] View schedule\n
            [0] Exit\n"""
    print(home)
    return int(input("StudentVUE> "))

def handle_gradebook():
    selection = 1
    while (selection != 0):
        print("Info related to grades")
        print("[1] View Gradebook for a Class\n[2] View Overall Grades\n[0] Exit")
        selection = int(input("StudentVUE\Gradebook> "))
        print(" ")
        if (selection == 1):
            period = int(input("What period would you like to view? "))
            get_assignments(sv, get_classID()[period - 1])
        elif (selection == 2): 
            print(get_gradebook())
        elif (selection == 0):
            return 0
        else:
            print("Error, Invalid Selection")
            return 1
def handle_assignments(period):
    selection = 1
    while(selection != 0):
        print("Info related to course assignments")
        
        print(get_info(sv, period))
        categories = get_categories(get_classID()[period - 1])
        assignments = get_assignments(sv, get_classID()[period - 1])
        print(categories.to_string(index=False))
        print(assignments.to_string(index=False))
        print("\n\n[1] View another class\n[2] Save assignments to .csv file\n[3] Save categories to .csv file\n[0] Exit\n")
        selection = int(input("StudentVUE\Assignments> "))
        if (selection == 1):
            period = int(input("Enter a class period: "))
            handle_assignments(period)
        if (selection == 2):
            print(handle_csv(assignments, get_info(sv, period)))
            time.sleep(3)
        if (selection == 3):
            print(handle_csv(categories, get_info(sv, period)))
            time.sleep(3)
        if (selection == 0):
            return 0
        else:
            print("Error, Invalid Selection")
            return 1

    

def main():
    global running
    while running:
        response = main_page()

        print(" ")
        os.system('cls')
        if response == 1:
            handle_gradebook()
        elif response == 2:
            os.system('cls')
            #print("***0 period counts as 9th period***")
            period = int(input("Enter a period number: "))
            handle_assignments(period)
        elif response == 3:
            print("""\n
                [0] Exit\n""")
        elif (response == 0):
            print("Exiting...")
            running = False
        elif (response < 0 or response > 3):
            print("Error, Invalid Option")
            return 1
    
if __name__ == "__main__":
    main()
