import logging
import os

from datetime import datetime
from logic.helpers.configuration import Configuration

now = datetime.now().strftime( '%Y%m%d-%H%M%S' )
log_filename = f'out/logs/{now}.log'
os.makedirs( os.path.dirname( log_filename ), exist_ok=True )

logging.basicConfig( format='%(levelname).1s %(asctime)s %(message)s [%(name)s  - ln: %(lineno)d]',
                     level=Configuration.LOGGING_LEVEL, filename=log_filename, filemode='w' )

log_formatter = logging.Formatter( '%(levelname).1s %(asctime)s %(message)s [%(name)s  - ln: %(lineno)d]' )
console_handler = logging.StreamHandler()
console_handler.setFormatter( log_formatter )
console_handler.setLevel( Configuration.LOGGING_LEVEL )
logging.getLogger( '' ).addHandler( console_handler )
