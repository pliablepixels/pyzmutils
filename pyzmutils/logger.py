from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import select
from sqlalchemy import or_
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

import configparser
import glob,os,psutil
import syslog
from inspect import getframeinfo,stack
import time
import pwd,grp
import datetime

#sudo -H pip install PyMySQL

class ZMLogger:
    connected = False
    levels = {
        'DBG':1,
        'INF':0,
        'WAR':-1,
        'ERR':-2,
        'FAT':-3,
        'PNC':-4,
        'OFF':-5
     }

    priorities = {
         'DBG':syslog.LOG_DEBUG,
         'INF':syslog.LOG_INFO,
         'WAR':syslog.LOG_WARNING,
         'ERR':syslog.LOG_ERR,
         'FAT':syslog.LOG_ERR,
         'PNC':syslog.LOG_ERR
     }

    def __init__(self, name=None, conf='/etc/zm'):
        self.pid =  os.getpid()
        self.process_name = name or psutil.Process(self.pid).name()
        syslog.openlog(logoption=syslog.LOG_PID)

        self.config = {
            'user' : None,
            'password' : None,
            'host' : None,
            'webuser': None,
            'webgroup': None,
            'dbname' : None,
            'logpath' : None,
            'log_level_syslog' : None,
            'log_level_file' : None,
            'log_level_db' : None,
            'log_debug' : None,
            'log_level_debug' : None,
            'log_debug_target' : None,
            'log_debug_file' :None,
            'server_id': None
        }

        # read all config files in order
        files=[]
        for f in glob.glob(conf+'/conf.d/*.conf'):
            files.append(f)
        files.sort()
        files.insert(0,conf+'/zm.conf')
        config_file = configparser.ConfigParser(interpolation=None)
        for f in files:
            with open(f) as s:
                #print ('reading {}'.format(f))
                config_file.read_string('[zm_root]\n' + s.read())

        # config_file will now contained merged data
        conf_data=config_file['zm_root']

        self.config['user'] = conf_data.get('ZM_DB_USER', 'zmuser')
        self.config['password'] = conf_data.get('ZM_DB_PASS', 'zmpass')
        self.config['webuser'] = conf_data.get('ZM_WEB_USER', 'www-data')
        self.config['webgroup'] = conf_data.get('ZM_WEB_GROUP', 'www-data')
        self.config['host'] = conf_data.get('ZM_DB_HOST', 'localhost')
        self.config['dbname'] = conf_data.get('ZM_DB_NAME', 'zm')
        self.config['logpath'] =  config_file['zm_root']['ZM_PATH_LOGS']


        self.cstr = 'mysql+pymysql://{}:{}@{}/{}'.format(self.config['user'],
            self.config['password'],self.config['host'],self.config['dbname'])

        try:
            engine = create_engine(self.cstr, pool_recycle=3600)
            self.conn = engine.connect()
            self.connected = True
        except SQLAlchemyError as e:
            self.connected = False
            syslog.syslog (syslog.LOG_ERR, self.format_string("Error connecting to DB:" + str(e)))
        
        #self.inspector = inspect(engine)
        #print(self.inspector.get_columns('Config'))
        meta = MetaData(engine,reflect=True)
        self.config_table = meta.tables['Config']
        self.log_table = meta.tables['Logs']

        select_st = select([self.config_table.c.Name, self.config_table.c.Value]).where(
                or_(self.config_table.c.Name=='ZM_LOG_LEVEL_SYSLOG',
                    self.config_table.c.Name=='ZM_LOG_LEVEL_FILE',
                    self.config_table.c.Name=='ZM_LOG_LEVEL_DATABASE',
                    self.config_table.c.Name=='ZM_LOG_DEBUG',
                    self.config_table.c.Name=='ZM_LOG_DEBUG_LEVEL',
                    self.config_table.c.Name=='ZM_LOG_DEBUG_FILE',
                    self.config_table.c.Name=='ZM_LOG_DEBUG_TARGET',
                    self.config_table.c.Name=='ZM_SERVER_ID',
                     ))
        resultproxy = self.conn.execute(select_st)
        db_vals = {row[0]:row[1] for row in resultproxy}

        self.config['log_level_syslog'] = int(db_vals['ZM_LOG_LEVEL_SYSLOG'])
        self.config['log_level_file'] = int(db_vals['ZM_LOG_LEVEL_FILE'])
        self.config['log_level_db'] = int(db_vals['ZM_LOG_LEVEL_DATABASE'])
        self.config['log_debug'] = int(db_vals['ZM_LOG_DEBUG'])
        self.config['log_level_debug'] = int(db_vals['ZM_LOG_DEBUG_LEVEL'])
        self.config['log_debug_file'] = db_vals['ZM_LOG_DEBUG_FILE']
        self.config['log_debug_target'] = db_vals['ZM_LOG_DEBUG_TARGET']
        self.config['server_id'] = db_vals.get('ZM_SERVER_ID',0)

        
        if self.config['log_level_file'] > self.levels['OFF']:
            n = os.path.split(self.process_name)[1].split('.')[0]
            self.log_fname = self.config['logpath']+'/'+n+'.log' 
            try:
                self.log_fhandle = open (self.log_fname,'a')
                uid = pwd.getpwnam(self.config['webuser']).pw_uid
                gid = grp.getgrnam(self.config['webgroup']).gr_gid
                os.chown(self.log_fname, uid,gid)
            except OSError as e:
                syslog.syslog (syslog.LOG_ERR, self.format_string("Error opening file log:" + str(e)))
                self.log_fhandle = None
                
        #print (self.config)

    def reconnect(self):
        try:
            self.conn.close()
        except:
            pass

        try:
            engine = create_engine(self.cstr, pool_recycle=3600)
            self.conn = engine.connect()
            #self.inspector = inspect(engine)
            #print(self.inspector.get_columns('Config'))
            meta = MetaData(engine,reflect=True)
            self.config_table = meta.tables['Config']
            self.log_table = meta.tables['Logs']
            message = 'reconnecting to Database...'
            log_string = '{level} [{pname}] [{msg}]'.format(level='INF', pname=self.process_name, msg=message)
            syslog.syslog (syslog.LOG_INFO, log_string)
        except SQLAlchemyError as e:
            self.connected = False
            syslog.syslog (syslog.LOG_ERR, self.format_string("Error connecting to DB:" + str(e)))
            return False
        else:
            self.connected = True
            return True
            

    def close(self):
        self.conn.close()
        syslog.closelog()
        if (self.log_fhandle): self.log_fhandle.close()

    def format_string(self,msg, level='ERR'):
        log_string = '{level} [{pname}] [{msg}]'.format(level=level, pname=self.process_name, msg=msg)
        return (log_string)
    
    def log(self,level, message, caller):
        # first stack element will be the wrapper log function
        # second stack element will be the actual calling function
        #print (len(stack()))
        if not caller:
            idx = min(len(stack()), 2) #incase someone calls this directly
            caller = getframeinfo(stack()[idx][0])
            #print ('Called from {}:{}'.format(caller.filename, caller.lineno))

        # write to syslog
        if self.levels[level] <= self.config['log_level_syslog']:
            log_string = '{level} [{pname}] [{msg}]'.format(level=level, pname=self.process_name, msg=message)
            syslog.syslog (self.priorities[level], log_string)

        # write to db
        if self.levels[level] <= self.config['log_level_db']:
            if not self.connected:
                syslog.syslog (syslog.LOG_INFO, self.format_string("Trying to reconnect"))
                if not self.reconnect():
                    syslog.syslog (syslog.LOG_ERR, self.format_string("reconnection failed, not writing to DB"))
                return False

            log_string = '{level} [{pname}] [{msg}]'.format(level=level, pname=self.process_name, msg=message)
            component = self.process_name
            serverid = self.config['server_id']
            pid = self.pid
            l = self.levels[level]
            code = level
            line = caller.lineno

            try:
                cmd = self.log_table.insert().values(TimeKey=time.time(), Component=component, ServerId=serverid, Pid=pid, Level=l, Code=code, Message=message,File=os.path.split(caller.filename)[1], Line=line)
                self.conn.execute(cmd)
            except SQLAlchemyError as e:
                self.connected = False
                syslog.syslog (syslog.LOG_ERR, self.format_string("Error writing to DB:" + str(e)))

        # write to file components
        if self.levels[level] <= self.config['log_level_file']:
            timestamp = datetime.datetime.now().strftime('%x %H:%M:%S')
           # 07/15/19 10:10:14.050651 zmc_m8[4128].INF-zm_monitor.cpp/2516 [Driveway: images:218900 - Capturing at 3.70 fps, capturing bandwidth 98350bytes/sec]
            fnfl ='{}:{}'.format(os.path.split(caller.filename)[1], caller.lineno)
            log_string = '{timestamp} {pname}[{pid}] {level} {fnfl} [{msg}]\n'.format(timestamp=timestamp, level=level, pname=self.process_name, pid=self.pid, msg=message, fnfl=fnfl)
            if self.log_fhandle: self.log_fhandle.write(log_string)

    def Info(self,message,caller=None):
        self.log('INF',message,caller)

    def Debug(self, level, message,caller=None):
        target = self.config['log_debug_target']
        if target:
            targets = [x.strip().lstrip('_') for x in target.split('|')]
            # if current name does not fall into debug targets don't log
            if not any(map(self.process_name.startswith, targets)):
                return

        if self.config['log_debug'] and level <= self.config['log_level_debug']:
            self.log('DBG', message,caller)

    def Warning(self,message,caller=None):
        self.log('WAR',message,caller)

    def Error(self,message,caller=None):
        self.log('ERR',message,caller)
     
    def Fatal(self,message,caller=None):
        self.log('FAT',message,caller)
        self.close()
        exit(-1)

    def Panic(self,message,caller=None):
        self.log('PNC',message,caller)
        self.close()
        exit(-1)

if __name__=='__main__':
    logger = ZMLogger()
    logger.Warning('This is a Warning')
    logger.Info('This is an Info')
    logger.Debug(1,'This is a Debug 1')
    logger.Debug(3,'This is a Debug 3')
    #logger.Fatal('This is a Fatal message, and we will quit')

    logger.close()

