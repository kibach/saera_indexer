import sys
reload(sys)
sys.setdefaultencoding('UTF8')
import ConfigParser
from daemonize import Daemonize
from saera_utils import config


def read_cfg():
    config_parser = ConfigParser.ConfigParser()
    config_parser.read('saera.cfg')
    config.BASIC_CONFIG['mysql_host'] = config_parser.get('database', 'host', '127.0.0.1')
    config.BASIC_CONFIG['mysql_port'] = config_parser.getint('database', 'port')
    config.BASIC_CONFIG['mysql_user'] = config_parser.get('database', 'user', 'root')
    config.BASIC_CONFIG['mysql_pass'] = config_parser.get('database', 'pass', '')
    config.BASIC_CONFIG['mysql_db'] = config_parser.get('database', 'db', 'saera')
    config.BASIC_CONFIG['process_count'] = config_parser.getint('main', 'process_count')
    config.BASIC_CONFIG['pid_file'] = config_parser.get('main', 'pid_file', '/tmp/saera.pid')


def main():
    print 'Saera indexer 0.1 started'
    workfather.father_thread()

read_cfg()

from concurrency import workfather

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-f":
        main()
    else:
        daemon = Daemonize(app="saera_indexer", pid=config.BASIC_CONFIG['pid_file'], action=main)
        daemon.start()
