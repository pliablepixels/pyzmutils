### What

Python utilities for ZoneMinder projects

### Limitations
* Only for Python3
* Basic support for now

Current modules:
* Logger

### Usage

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

