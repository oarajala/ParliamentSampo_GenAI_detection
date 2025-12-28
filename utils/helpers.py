import os

def get_parent_directory() -> str:
    """Get the parent directory for handling csv files.

    Returns:
        string: the path to the directory where directories for csv files are located
    """
    #create relative path for parent
    relative_parent = os.path.join(os.getcwd(), '.')

    #use abspath for absolute parent path
    return str(os.path.abspath(relative_parent)).replace('\\', '/')