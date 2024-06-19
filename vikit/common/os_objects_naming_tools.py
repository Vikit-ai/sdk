
import os 
import random
import re


def get_canonical_name(file_path: str):
    """
    Get the canonical name of a file, without the extension
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def create_non_colliding_file_name(file_path: str = None, depth: int = 1):
    """
    Create a non-colliding name for a file, by adding a random suffix, and without file type extension

    Before creating the name we check it does not already exist in the target directory
    In case it does, we run a recursion on ourselves and increase the depth of the random boundary per a factor of x10

    :param file_path: the path of the file to be created
    :param depth: the depth of the recursion
    :return: the non-colliding name
    """
    target_name = get_canonical_name(file_path) + "_" + str(random.randint(0, 100))
    if not os.path.exists(target_name): 
        return target_name
    else:
        return create_non_colliding_file_name(file_path, depth * 10)
    

def get_safe_filename(filename):
    return re.sub(r'(?u)[^-\w.]', '', filename.strip().replace(' ', '_'))
