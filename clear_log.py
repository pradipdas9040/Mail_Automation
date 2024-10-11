import os
import yaml
import datetime
import sys

today = datetime.date.today().strftime('%d-%m')

try:
    if(today not in ['31-12', '31-05']):
        sys.exit(1) 

    # Function to read YAML file and get the extension
    def get_extension_from_yaml(yaml_file):
        with open(yaml_file, 'r') as file:
            config = yaml.safe_load(file)
            return config.get('log_extension')
    
    # Function to find files with the specified extension
    def find_files_with_extension(extension, directory='.'):
        log_files = [f for f in os.listdir(directory) if f.endswith(extension)]
        return log_files[0]
    
    def clear_log(file_path):
        # Open the file in write mode to clear it
        with open(file_path, 'w') as file:
            pass  # No content is written, so the file is cleared
        print('log refreshed')
    
    log_extension = os.getenv('LOG_EXTENSION', '.log')
    
    print(f'log file extension:{log_extension}')
    
    # Search for log files in the current directory
    log_files = find_files_with_extension(log_extension)
    
    if (log_files != None):
        clear_log(log_files)
except:
    pass
