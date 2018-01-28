#!/usr/bin/python
import os
import sys
import traceback
import json

try:
	CONFIG=json.load(open('config.json'))
except IOError:
	print "Can't load config from file"
	exit()
except:
	traceback.print_exc()


TEMPLATE = '''#!/bin/sh /etc/rc.common
START=95
SERVICE_USE_PID=1
SERVICE_WRITE_PID=1
SERVICE_DAEMONIZE=1
start() {
        #service_start /usr/bin/ss-local -s server_ip -p server_port -l local_port -k password -m method -t timeout -b 0.0.0.0
        service_start /usr/bin/ss-redir -s server_ip -p server_port -l local_port -k password -m method -t timeout -b 0.0.0.0 -u
        service_start /usr/bin/ss-tunnel -s server_ip -p server_port -l local_port -k password -m method -t timeout -b 0.0.0.0 -l 5353 -L 8.8.8.8:53 -u
}
stop() {
        #service_stop /usr/bin/ss-local
        service_stop /usr/bin/ss-redir
        service_stop /usr/bin/ss-tunnel
}
'''


def start(name):
	try:
		instance_config = CONFIG[name]
		config = TEMPLATE.replace('server_ip', instance_config['server']).replace('server_port', instance_config[
			'server_port']).replace('local_port', instance_config['local_port']).replace('password', instance_config[
			'password']).replace('method', instance_config['method']).replace('timeout', instance_config['timeout'])
		os.system('/etc/init.d/shadowsocks stop')
		f = open('/etc/init.d/shadowsocks', 'w')
		f.write(config)
		f.close()
		os.system('/etc/init.d/shadowsocks start')
		return True
	except KeyError:
		print 'No such instance:%s' % name
		return False
	except:
		traceback.print_exc()

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print 'Example:\n%s show\t\t\t\tshow available instance\n%s start (INSTANCE)\tstart an instance\n%s stop\t\t\t\tstop current service' % (
		sys.argv[0], sys.argv[0], sys.argv[0])
	elif sys.argv[1] == 'show':
		for instance in CONFIG.keys():
			print '%s:%s' % (instance, CONFIG[instance]['server'])
	elif sys.argv[1] == 'start':
		try:
			if start(sys.argv[2]):
				print '\033[0;32mStart %s successfully\033[0m'%sys.argv[2]
			else:
				print '\033[0;31mFailed to start %s\033[0m'%sys.argv[2]
		except IndexError:
			print 'Please input an instance name'
		except:
			traceback.print_exc()
	elif sys.argv[1] == 'stop':
		os.system('/etc/init.d/shadowsocks stop')
