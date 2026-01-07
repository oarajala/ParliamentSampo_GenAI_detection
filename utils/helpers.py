import os
from datetime import timedelta, datetime, date

def get_parent_directory() -> str:
    """Get the parent directory for handling csv files.

    Returns:
        string: the path to the directory where directories for csv files are located
    """
    #create relative path for parent
    relative_parent = os.path.join(os.getcwd(), '.')

    #use abspath for absolute parent path
    return str(os.path.abspath(relative_parent)).replace('\\', '/')

def calculate_electoral_term_progression(date: str, electoral_term: str) -> int:
    """Added data validation due to missing values in 2011 raw csv.
    """
    if (date is None) or (electoral_term is None):
        return None
    if (type(date) != str) or (type(electoral_term) != str):
        return None
    elif ((date is not None) and (date.strip() == '')) or ((electoral_term is not None) and (electoral_term.strip() == '')):
        return None
    else:
        dt_date = datetime.strptime(date, "%Y-%m-%d")
        dt_et_start = datetime.strptime(electoral_term[:10], "%Y-%m-%d")
        dt_et_end = datetime.strptime(electoral_term[11:], "%Y-%m-%d")

        # calculate the length of the electoral term, store as days
        et_length = (dt_et_end-dt_et_start)
        et_length = et_length.days

        # calculate the time in days to the end of the electoral term
        days_to_end_of_term = dt_et_end-dt_date
        days_to_end_of_term = days_to_end_of_term.days

        # calculate the time served of the electoral term at the time of date (speech) in days
        days_serverd_from_total_et = et_length-days_to_end_of_term

        # calculate the progression of the electoral term relative to the date (speech)
        progression = int(round((days_serverd_from_total_et/et_length)*100, 0))

        return progression