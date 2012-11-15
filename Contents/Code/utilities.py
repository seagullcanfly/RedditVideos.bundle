# Reddit Video Utilities


def list_to_string(l):
    ''' We convert the list to a string
    to create a summary for the field.'''
    s = ''
    for element in sorted(l):
        s += ' * '
        s += element
    return s


def good_url(url):
    ''' This will filter out unwanted words in the url.'''
    return ('playlist' not in url) and ('crackle.com' not in url) and url


def create_list(d):
    ''' This flattens the lists from the master dictionary.
    We use this master list in "all subreddits."'''
    master_list = []
    for key in d:
        master_list += d[key]['c_list']
    return sorted(master_list)
