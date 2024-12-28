#!/bin/sh
# chkconfig: 123456 90 10
# PaperPi Service Launcher
#
export PATH="$(pwd)/.venv/bin:$PATH"

start() {
    python3 service.py &
    echo "PaperPi Service started."
}

stop() {
    pid=`ps -ef | grep '[p]ython service.py' | awk '{ print $2 }'`
    echo $pid
    kill $pid
    sleep 2
    deactivate
    echo "PaperPi Service killed."
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  *)
    echo "Usage: /etc/init.d/paperPi.sh {start|stop|restart}"
    exit 1
esac
exit 0