### What

Python utilities for ZoneMinder projects

### Limitations
* Only for Python3
* Basic support for now

Current modules:
* Logger

### Usage

#### Basic
```python
import pyzmutils.logger as zmlog

logger = zmlog.ZMLogger()
# You can also specify a module name and a conf path manually
# if you don'y specify a module name, then the process name is taken
# logger = zmlog.ZMLogger(name='mymodule', conf='/etc/zm')

logger.Warning('This is a Warning')
logger.Info('This is an Info')
logger.Debug(1,'This is a Debug 1')
logger.Debug(3,'This is a Debug 3')
logger.Fatal('This is a Fatal message, and we will quit')
logger.close()
```

#### Advanced

You can customize the constructor like so:

```python

import pyzmutils.logger as zmlog
overrides = {
  'conf_path':'/my/special/zm/config/path', # default is /etc/zm
  'driver': 'mysql+pymysql', # default is mysql+mysqldb see https://docs.sqlalchemy.org/en/13/dialects/mysql.html
}
logger = zmlog.ZMLogger(name='myapp', overrides=overrides)
```

Basically, overrides will override values this module retrieves from the conf of ZM DB. Keys available to override:

```
  'conf_path': '/etc/zm',
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
  'server_id': None,
  'driver': 'mysql+mysqldb'
```

So for example, let's suppose ZM has DB logging enabled, but you want to turn it off for this model. Also, ZM uses syslog as INFO but you want DEBUG3 for this module:

you'd do:

```python

overrides = {
    'log_level_db': -5, # -5 is 'OFF' in ZM
    'log_level_syslog': 1, # 1 is 'DBG' in ZM
    'log_level_debug': 3,
    'log_debug_target': 'myapp'
    }
logger = ZMLogger(name='myapp', overrides=overrides)
print (logger.get_config())
logger.Warning('This is a Warning')
logger.Info('This is an Info')
logger.Debug(1,'This is a Debug 1')
logger.Debug(3,'This is a Debug 3')
#logger.Fatal('This is a Fatal message, and we will quit')
logger.close()

```
