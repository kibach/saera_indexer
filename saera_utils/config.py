BASIC_CONFIG = {}


def get_mysql_url():
    return 'mysql://' + BASIC_CONFIG['mysql_user'] + ':' + BASIC_CONFIG['mysql_pass'] + \
           '@' + BASIC_CONFIG['mysql_host'] + ':' + str(BASIC_CONFIG['mysql_port']) + '/' + BASIC_CONFIG['mysql_db']
