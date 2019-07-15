### What

Python utilities for ZoneMinder projects

Current modules:
* Logger

### Usage

```python
import pyzmutils.logger as zmlog

logger = zmlog.ZMLogger()
logger.Warning('This is a Warning')
logger.Info('This is an Info')
logger.Debug(1,'This is a Debug 1')
logger.Debug(3,'This is a Debug 3')
logger.Fatal('This is a Fatal message, and we will quit')
logger.close()
```

