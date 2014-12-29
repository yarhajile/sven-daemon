from distutils.core import setup

setup(
    name = 'Sven Control Daemon',
    version = '1.0',
    packages = [ 'Sven', 'Sven.Cloud', 'Sven.System', 'Sven.ArduinoUno', 'Sven.RaspberryPi', 'Sven.BeagleboneBlack',
                 'Sven.BeagleboneBlack.Adafruit_BBIO-0.0.19', 'Sven.BeagleboneBlack.Adafruit_BBIO-0.0.19.test',
                 'Sven.BeagleboneBlack.Adafruit_BBIO-0.0.19.overlays',
                 'Sven.BeagleboneBlack.Adafruit_BBIO-0.0.19.Adafruit_BBIO' ],
    url = 'http://www.svencontrol.com',
    license = 'Proprietary',
    author = 'Elijah Ethun',
    author_email = 'elijahe@gmail.com',
    description = ''
)
