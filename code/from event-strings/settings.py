# def init(*, log_level = 'ALL', strict_mode = False): # correct way, but pylint complains
def init(log_level = 'ALL', strict_mode = False):
    global __LOG_LEVELS
    global __log_level
    global __strict_self_referent_mode
    global __issue_log
    __LOG_LEVELS = dict(ALL=3, WARN_INFO=2, INFO=1, NONE=0)
    __log_level = __LOG_LEVELS[log_level]
    __strict_self_referent_mode = strict_mode
    __issue_log = []

def is_issue_found():
    global __issue_log
    return len(__issue_log) > 0

def issue_found(issue_level, issue_message):
    global __issue_log
    __issue_log.append({'level': issue_level, 'message': issue_message})

def clear_issues():
    global __issue_log
    __issue_log = []

def log_issues(log_file = None):
    if log_file is None:
        for i in __issue_log:
            print('\033[93m> {}\033[0m'.format(i['message']))
