def get_grade(score):
    if score >= 80 and score <= 100:
        return 'A'
    elif score >= 75:
        return 'B'
    elif score >= 70:
        return 'B+'
    elif score >= 65:
        return 'C+'
    elif score >= 60:
        return 'C'
    elif score >= 55:
        return 'D+'
    elif score >= 50:
        return 'D'
    elif score >= 45:
        return 'E'
    else:
        return 'F'
    
def main():
    print("\n--- UG School Grading System ---")
    student_name = input("Enter the student's name: ")
    course = input("Enter the course name: ")
    score = float(input("Enter the student's score: "))
    if score < 0 or score > 100:
        print("Invalid score. Please enter a score between 0 and 100.")
        return
    grade = get_grade(score)
    print("\n--- Student Grade Report ---")
    print(f"Student: {student_name}")
    print(f"Course: {course}")
    print(f"Score: {score}")
    print(f"Grade: {grade}")

main()