
import os



def get_all_files(path, contains=''):
    files = os.listdir(path)
    files = [os.path.join(path, file_name) for file_name in files]
    
    file_paths = [file_path for file_path in files if os.path.isfile(file_path)]
    file_paths = [file_path for file_path in file_paths if contains in file_path]
    dir_paths = [dir_path for dir_path in files if os.path.isdir(dir_path)]

    for dir_path in dir_paths:
        file_paths.extend(get_all_files(dir_path, contains=contains))
    
    return file_paths