import re

def cutcontent(content):
    return list(filter(lambda x: x.strip() != '', re.split('；|。', content)))
