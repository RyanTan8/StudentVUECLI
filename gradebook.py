from collections import OrderedDict
from studentvue import StudentVue
def login():
    print("Enter Credentials: ")
    username = ""# Your StudentVUE username
    password = "" # Your StudentVUE password
    domain = "" # Your StudentVUE district's domain
    return StudentVue(username, password, domain)
sv = login()


print(sv.get_student_info())
print(sv.get_gradebook())

