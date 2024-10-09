def average_grade():
    grades = [None, None, None]

    valid_grades = list()

    for grade in grades:
        if grade is not None:
            valid_grades.append(grade)

    if len(valid_grades) > 0:
        return round(sum(valid_grades) / len(valid_grades), 2)
    
    return None

print(average_grade())