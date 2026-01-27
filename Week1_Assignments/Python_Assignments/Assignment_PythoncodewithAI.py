# Creating a python  code using AI
# Ideate : Based on the average calulated from the majors, decide which group of studies they will join.
# prompt
    # Role: You are a python developer
    # Goal: 
        # I want to get marks from 5 different students on major subjects Maths, science and Physics and take the average. 
        # Based on the average i want to decide which study group they will belong to - Group 1, Group 2 or Group 3
    # Logics:
        # average >=75 = Group 1
        # average >=50 = Group 2
        # average >=35 = Group 3
        # average <35 = Not eligible
        # print the student has failed and not eligle for joining any group if scored < 35 even in any one of the subject.
        # In this case do not considr the avg mark.
        # Dont get the inputs from user, instead store the valus in a varible and show the final results. 
    # Conditions:
        # write me a fully functional code to achieve the above goal with step by step proedure to execute them in VS Code.
        # i am new t this python development so take care of all implementation required and avoid possible erros.
        # add comments to each block of code for beter underderstanding
# running code in VS code

# ---------------------------------------------
# Program: Student Study Group Classification
# Using Stored Data (No User Input)
# ---------------------------------------------

# Store student data in a list of dictionaries
students = [
    {"name": "Ravi", "maths": 80, "science": 75, "physics": 70},
    {"name": "Anu", "maths": 60, "science": 55, "physics": 58},
    {"name": "Kiran", "maths": 40, "science": 30, "physics": 45},
    {"name": "Meena", "maths": 72, "science": 78, "physics": 80},
    {"name": "Arun", "maths": 34, "science": 50, "physics": 60}
]

# Loop through each student
for student in students:

    name = student["name"]
    maths = student["maths"]
    science = student["science"]
    physics = student["physics"]

    print("\n---------------------------------")
    print(f"Student Name: {name}")

    # FAIL condition: any subject < 35
    if maths < 35 or science < 35 or physics < 35:
        print("Status: FAILED")
        print("Result: Not eligible for any group")
        continue  # Skip average calculation

    # Calculate average marks
    average = (maths + science + physics) / 3
    print(f"Average Marks: {average:.2f}")

    # Decide study group
    if average >= 75:
        print("Assigned Group: Group 1")

    elif average >= 50:
        print("Assigned Group: Group 2")

    elif average >= 35:
        print("Assigned Group: Group 3")

    else:
        print("Result: Not eligible for any group")

# End of program
