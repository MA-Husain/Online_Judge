import subprocess
import os
import re
from pathlib import Path
import uuid
from django.conf import settings
from django.shortcuts import render
from .models import Submission, SubmissionTestCase
import math
import psutil
from subprocess import PIPE, Popen, TimeoutExpired
import time

# Function to remove all files in a directory
def clear_directory(directory_path):
    dir_path = Path(directory_path)
    for file in dir_path.iterdir():
        try:
            # Close any open file handles
            with open(file, 'r') as f:
                pass  # Just open and close to ensure it's not in use

            # Ensure the file is not in use
            if file.suffix in ['.exe', '.class']:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] == file.name:
                        proc.terminate()
                        proc.wait()
            file.unlink()
        except PermissionError as e:
            pass
        except Exception as e:
            pass
            


def compare_outputs(expected, generated):
    # Strip leading/trailing whitespace and normalize newlines
    expected = expected.strip().splitlines()
    generated = generated.strip().splitlines()

    # Compare line by line
    for exp_line, gen_line in zip(expected, generated):
        # Compare as floats if possible
        try:
            exp_val = float(exp_line)
            gen_val = float(gen_line)
            if not math.isclose(exp_val, gen_val, rel_tol=1e-4):  # Adjust tolerance as needed
                return False
        except ValueError:
            if exp_line != gen_line:
                return False

    return len(expected) == len(generated)

def save_file(content, file_path):
    # Strip leading/trailing whitespace and replace multiple newlines with a single newline
    content = content.strip()
    content = re.sub(r'\r?\n+', '\n', content)  # Normalize newlines to Unix-style
    with open(file_path, 'w', newline='\n') as file:
        file.write(content)
    
def compile_code(code_path, language):
    code_path = Path(code_path)
    if language == 'java':
        compile_command = ["javac", str(code_path)]
    elif language == 'cpp':
        executable_path = code_path.with_suffix('.exe')
        compile_command = ["g++", str(code_path), "-o", str(executable_path)]

    try:
        # Compile the code if necessary
        compile_process = subprocess.run(compile_command, capture_output=True, text=True, timeout=10)
        if compile_process.returncode != 0:
            error_message = f"Compilation failed: {compile_process.stderr}"
            return 0, error_message
        else:
            return 1, "Compiled Successfully"
    except subprocess.TimeoutExpired:
        error_message = "Compilation time limit exceeded."
        return 0, error_message
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return 0, error_message
    
def run_code(code_path, input_path, output_path, language):
    code_path = Path(code_path)
    input_path = Path(input_path)
    output_path = Path(output_path)
    memory_limit=1024 * 1024 * 256

    if language == 'java':
        class_name = code_path.stem
        run_command = ["java", "-cp", str(code_path.parent), class_name]
    elif language == 'cpp':
        executable_path = code_path.with_suffix('.exe')
        run_command = [str(executable_path)]
    elif language == 'py':
        run_command = ["python", str(code_path)]
    try:
        # Run the code
        with open(output_path, 'w') as output_file, open(input_path) as input_file:
            process = Popen(run_command, stdin=input_file, stdout=output_file, stderr=PIPE, text=True)
            psutil_process = psutil.Process(process.pid)
            start_time = time.time()

            while process.poll() is None:
                memory_usage = psutil_process.memory_info().rss
                if memory_usage > memory_limit:
                    process.terminate()
                    output_file.write(f"Memory limit exceeded ({memory_limit} bytes)\n")
                    break
                if time.time() - start_time > 1:
                    process.terminate()
                    output_file.write("Execution time limit exceeded.\n")
                    break
                time.sleep(0.1)

            # Ensure the process is terminated
            process.terminate()
            process.communicate()

            if process.returncode != 0:
                error_message = f"Execution failed: {process.stderr}"
                save_file(error_message, output_path)


        if not output_path.exists():
            save_file(f"Output file not found: {output_path}", output_path)

    except subprocess.TimeoutExpired:
        save_file("Execution time limit exceeded.", output_path)
    except Exception as e:
        save_file(f"An error occurred: {str(e)}", output_path)
    finally:
        # Ensure process termination and file handle cleanup
        if process and process.poll() is None:
            process.terminate()
            process.communicate()
        psutil_process = None  # Clear the psutil process handle

        # Ensure file handles are closed
        if 'input_file' in locals() and not input_file.closed:
            input_file.close()
        if 'output_file' in locals() and not output_file.closed:
            output_file.close()
    

def handle_run(request, form, problem):
    language = form.cleaned_data['language']
    code = form.cleaned_data['code']
    input_data = form.cleaned_data['input_data']
    unique_id = str(uuid.uuid4())

    # Define the directories
    input_dir = os.path.join(settings.BASE_DIR, 'coding', 'run', 'input')
    code_dir = os.path.join(settings.BASE_DIR, 'coding', 'run', 'code')
    output_dir = os.path.join(settings.BASE_DIR, 'coding', 'run', 'generated_output')

    input_file_path = os.path.join(input_dir, f'{unique_id}.txt')
    code_file_path = os.path.join(code_dir, f'Main.{language}')
    output_file_path = os.path.join(output_dir, f'{unique_id}.txt')

    save_file(input_data, input_file_path)
    save_file(code, code_file_path)

    if language in ['cpp', 'java']:
        compile_status,output_data = compile_code(code_file_path, language)
        if compile_status == 0:
            # Clear the directories
            clear_directory(input_dir)
            clear_directory(code_dir)
            clear_directory(output_dir)
            return render(request, 'coding/submit_code.html', {
            'problem': problem,
            'form': form,
            'output_data': output_data,
            'run': True
        })
    
    run_code(code_file_path, input_file_path, output_file_path, language)

    with open(output_file_path, 'r') as file:
        output_data = file.read()
    
    # Clear the directories
    clear_directory(input_dir)
    clear_directory(code_dir)
    clear_directory(output_dir)

    return render(request, 'coding/submit_code.html', {
        'problem': problem,
        'form': form,
        'output_data': output_data,
        'run': True
    })

def handle_submit(request, form, problem, pk):
    language = form.cleaned_data['language']
    code = form.cleaned_data['code']
    submission = Submission.objects.create(
        user=request.user,
        problem=problem,
        code=code,
        language=language,
        status='Pending'
    )

    submission_folder = os.path.join(settings.BASE_DIR, 'coding', 'submissions', str(submission.id))
    input_folder = os.path.join(submission_folder, 'input')
    code_folder = os.path.join(submission_folder, 'code')
    generated_output_folder = os.path.join(submission_folder, 'generated_output')
    expected_output_folder = os.path.join(submission_folder, 'expected_output')

    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(code_folder, exist_ok=True)
    os.makedirs(generated_output_folder, exist_ok=True)
    os.makedirs(expected_output_folder, exist_ok=True)

    code_file_path = os.path.join(code_folder, f'Main.{language}')
    save_file(code, code_file_path)
    
    if language in ['cpp', 'java']:
        compile_status,  generated_output_data = compile_code(code_file_path, language)
        if compile_status == 0:
            if generated_output_data == "Compilation time limit exceeded.":
                submission.status = 'Time Limit Exceeded while compilation'
            else:
                submission.status = f'Wrong answer on test case {1}'
            submission.save()
            clear_directory(input_folder)
            clear_directory(code_folder)
            clear_directory(generated_output_folder)
            clear_directory(expected_output_folder)
            os.rmdir(input_folder)
            os.rmdir(code_folder)
            os.rmdir(generated_output_folder)
            os.rmdir(expected_output_folder)
            os.rmdir(submission_folder)
            return render(request, 'coding/submit_code.html', {
                'problem': problem,
                'submission': submission,
                'submission_done': True
            })
    

    i = 1
    for test_case in problem.test_cases.all():

        input_data = test_case.input.strip()
        input_data = re.sub(r'\r?\n+', '\n', input_data)

        expected_output_data = test_case.expected_output.strip()
        expected_output_data = re.sub(r'\r?\n+', '\n', expected_output_data)

        unique_id = str(uuid.uuid4())
        input_file_path = os.path.join(input_folder, f'{unique_id}.txt')
        generated_output_file_path = os.path.join(generated_output_folder, f'{unique_id}.txt')
        expected_output_file_path = os.path.join(expected_output_folder, f'{unique_id}.txt')

        save_file(input_data, input_file_path)
        save_file(expected_output_data, expected_output_file_path)

        run_code(code_file_path, input_file_path, generated_output_file_path, language)

        with open(generated_output_file_path, 'r') as file:
            generated_output_data = file.read()
            generated_output_data = re.sub(r'\r?\n+', '\n', generated_output_data)


        is_passed = compare_outputs(expected_output_data, generated_output_data)

        SubmissionTestCase.objects.create(
            submission=submission,
            test_case=test_case,
            is_passed=is_passed
        )

        if not is_passed:
            if generated_output_data == "Execution time limit exceeded.":
                submission.status = f'Time Limit Exceeded on test case {i}'
            else:
                submission.status = f'Wrong answer on test case {i}'
            break

        i += 1

    if submission.status == 'Pending':
        submission.status = 'Accepted'

    submission.save()

    submission_test_cases = submission.submission_test_cases.all()

    response = render(request, 'coding/submit_code.html', {
        'problem': problem,
        'submission': submission,
        'submission_done': True,
        'submission_test_cases': submission_test_cases
    })

    # Clean up files
    clear_directory(input_folder)
    clear_directory(code_folder)
    clear_directory(generated_output_folder)
    clear_directory(expected_output_folder)
    os.rmdir(input_folder)
    os.rmdir(code_folder)
    os.rmdir(generated_output_folder)
    os.rmdir(expected_output_folder)
    os.rmdir(submission_folder)

    submission_test_cases.delete()

    return response
