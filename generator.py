from openai import OpenAI
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    with open("problems/p1/description.txt", "r") as f:
        problem_description = f.read()
    with open("problems/p1/student_code.py", "r") as f:
        student_code = f.read()
    with open("problems/p1/edit.txt", "r") as f:
        edit = f.read()
    filled_template = populate_teacher_template(problem_description,student_code,edit)
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"{filled_template}"},
        ],
    )
    with open("problems/p1/teacher.txt", "w") as f:
        f.write(completion.choices[0].message.content)
    # Extract the long form hint
    
    long_form_hint = extract_long_form_hint("problems/p1/teacher.txt")
    
    
    filled_student_template = populate_student_template(long_form_hint, student_code)
    
    completion_student = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"{filled_student_template}"},
        ],
    )
    with open("problems/p1/student.txt", "w") as f:
        f.write(completion_student.choices[0].message.content)
    

def populate_teacher_template(problem_description, student_code, edit):
    with open("prompt/teacher.txt", "r") as f:
        teacher_template = f.read()
    filled_template = teacher_template.format(
        problem_description=problem_description,
        student_code=student_code,
        edit=edit,
    )
    return filled_template

def populate_student_template(long_form_hint, student_code):
    with open("prompt/student.txt", "r") as f:
        student_template = f.read()
    filled_student_template = student_template.format(
        student_code=student_code,
        long_form_hint=long_form_hint,
    )
    return filled_student_template
    
def extract_long_form_hint(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Find the start of the long-form hint
    start_index = content.find("Long-form hint:") + len("Long-form hint:")
    
    # Find the start of the short-form hint (which marks the end of the long-form hint)
    end_index = content.find("Short-form hint:")
    
    # Extract and strip any leading/trailing whitespace
    long_form_hint = content[start_index:end_index].strip()
    
    return long_form_hint


if __name__ == "__main__":
    main()
