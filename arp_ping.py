import re
import csv
import subprocess
import concurrent.futures
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import os

RESULTS_DIR = ''

def parse_hosts(output):
    pattern = r'Internet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+'
    matches = re.findall(pattern, output)
    return matches

def check_host(host):
    try:
        subprocess.check_output(['ping', '-n', '2', '-w', '2', host])
        return 'reachable'
    except subprocess.CalledProcessError:
        return 'unreachable'

def browse_file():
    filename = filedialog.askopenfilename(filetypes=(('Text Files', '*.txt;*.rtf;*.csv'), ('All Files', '*.*')))

    if filename:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)

def process_file():
    filename = file_entry.get()

    if not filename:
        result_label.config(text='Please select a file.')
        return

    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    if before_var.get():
        results_file = f'before_{time_str}_results.csv'
    else:
        results_file = f'after_{time_str}_results.csv'

    with open(filename, 'r') as f:
        if filename.endswith('.csv'):
            reader = csv.reader(f)
            hosts = [row[0] for row in reader]
        else:
            output = f.read()
            hosts = parse_hosts(output)

    results_file = os.path.join(RESULTS_DIR, results_file)

    with open(results_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Host', 'Result'])

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for host in hosts:
                futures.append(executor.submit(check_host, host))
            for i, host in enumerate(hosts):
                result = futures[i].result()
                writer.writerow([host, result])

    result_label.config(text=f'Results written to {results_file}.')


def compare_files():
    # Use the RESULTS_DIR and os.listdir() to find the latest before and after files
    # before_files = sorted([f for f in os.listdir(RESULTS_DIR) if f.startswith('before_')])
    # after_files = sorted([f for f in os.listdir(RESULTS_DIR) if f.startswith('after_')])
    # if before_files:
    #     default_before_file = before_files[-1]
    # else:
    #     default_before_file = ''
    # if after_files:
    #     default_after_file = after_files[-1]
    # else:
    #     default_after_file = ''

    # Call the browse_file function with the default files and the RESULTS_DIR as the default directory
    # browse_file_entry(before_file_entry, default_file=default_before_file, default_dir=RESULTS_DIR)
    # browse_file_entry(after_file_entry, default_file=default_after_file, default_dir=RESULTS_DIR)

    before_file = before_file_entry.get()
    after_file = after_file_entry.get()
    if not before_file or not after_file:
        compare_label.config(text='Please select both files.')
        return

    with open(before_file, 'r') as f1, open(after_file, 'r') as f2:
        before_reader = csv.reader(f1)
        after_reader = csv.reader(f2)
        before_rows = [row for row in before_reader]
        after_rows = [row for row in after_reader]

    diff_rows = []
    for i in range(len(before_rows)):
        before_host, before_result = before_rows[i]
        after_host, after_result = after_rows[i]
        if before_host != after_host:
            raise ValueError('Host lists are not identical.')
        if before_result != after_result:
            diff_rows.append([before_host, before_result, after_result])

    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    diff_results_file = os.path.join(RESULTS_DIR, f'diff_results_{time_str}.csv')
    with open(diff_results_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Host', 'Before', 'After'])
        for row in diff_rows:
            writer.writerow(row)

    compare_label.config(text=f'Differences written to {diff_results_file}.')

    # Open the diff_results file using the appropriate method for the operating system
    if os.name == 'nt':  # If running on Windows
        os.startfile(diff_results_file)  # Open the diff_results file using the default application
    elif os.name == 'posix':  # If running on macOS or Linux
        os.system(f'open {diff_results_file}')  # Open the diff_results file using the default application on macOS


window = tk.Tk()
window.title('Host Checker')
file_label = tk.Label(window, text='Select ARP input file:')
file_entry = tk.Entry(window, width=50)
file_button = tk.Button(window, text='Browse', command=browse_file)
before_label = tk.Label(window, text='Run before:')
before_var = tk.BooleanVar(value=True)
before_checkbutton = tk.Checkbutton(window, variable=before_var)
process_button = tk.Button(window, text='Process', command=process_file)
result_label = tk.Label(window, text='')
compare_label = tk.Label(window, text='Compare before and after results:')
before_file_label = tk.Label(window, text='Before:')
before_file_entry = tk.Entry(window, width=50)
before_file_button = tk.Button(window, text='Browse', command=lambda: browse_file_entry(before_file_entry))
after_file_label = tk.Label(window, text='After:')
after_file_entry = tk.Entry(window, width=50)
after_file_button = tk.Button(window, text='Browse', command=lambda: browse_file_entry(after_file_entry))
compare_button = tk.Button(window, text='Compare', command=compare_files)

file_label.grid(row=0, column=0, padx=5, pady=5)
file_entry.grid(row=0, column=1, padx=5, pady=5)
file_button.grid(row=0, column=2, padx=5, pady=5)
before_label.grid(row=1, column=0, padx=5, pady=5)
before_checkbutton.grid(row=1, column=1, padx=5, pady=5)
process_button.grid(row=2, column=0, padx=5, pady=5)
result_label.grid(row=2, column=1, padx=5, pady=5)
compare_label.grid(row=3, column=0, padx=5, pady=5)
before_file_label.grid(row=4, column=0, padx=5, pady=5)
before_file_entry.grid(row=4, column=1, padx=5, pady=5)
before_file_button.grid(row=4, column=2, padx=5, pady=5)
after_file_label.grid(row=5,column=0, padx=5, pady=5)


after_file_entry.grid(row=5, column=1, padx=5, pady=5)
after_file_button.grid(row=5, column=2, padx=5, pady=5)
compare_button.grid(row=6, column=0, padx=5, pady=5)

def browse_file_entry(entry, default_file='', default_dir=RESULTS_DIR):
    if default_file:
        dirname = os.path.dirname(default_file)
    elif default_dir:
        dirname = default_dir
    else:
        dirname = os.getcwd()

    filename = filedialog.askopenfilename(
        filetypes=(('CSV Files', '*.csv'), ('All Files', '*.*')),
        initialdir=dirname,
        initialfile=default_file
    )

    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

window.mainloop()
