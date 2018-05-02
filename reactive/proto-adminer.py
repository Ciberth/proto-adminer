import pwd
import os
from subprocess import call
from charmhelpers.core.hookenv import log, status_set
from charmhelpers.core.templating import render
from charms.reactive import when, when_not, set_flag, clear_flag

@when('website.available')
def configure_port(website):
    log("poort functie")
    website.configure(port=hookenv.config('port'))

@when('website.available', 'mysqldatabase.connected')
def request_db(database):
    database.configure('proto', 'admin', 'admin', prefix="proto")
    log("db requested")

@when('website.available', 'mysqldatabase.available')
def setup_app(mysql):
    render(source='mysql_configure.php',
        target='/var/www/proto-adminer/mysql_configure.php',
        owner='www-data',
        perms=0o775,
        context={
            'db': mysql,
        })
    log("in setup function")
    set_flag('apache.start')
    status_set('maintenance', 'Setting up application')


@when('website.available')
@when_not('mysqldatabase.connected')
def no_mysql_relation():
    status_set('waiting', 'Waiting for mysql relation')


@when('mysqldatabase.connected')
@when_not('mysqldatabase.available')
def mysql_connected_but_waiting(mysql):
    status_set('waiting', 'Waiting for mysql service')

@when('website.started')
def apache_started():
    status_set('active', 'Ready')
