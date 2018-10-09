from fabric.api import task, hide, env, run, execute, sudo
from fabric.colors import green, yellow, red
from fabric.contrib.console import confirm

from dev_cli.aws.ec2 import create_ec2_instance, start_ec2_instance, stop_ec2_instance, \
    terminate_ec2_instance, get_ec2_instance, filter_ec2_instances
from dev_cli.aws.route53 import create_subdomain
from dev_cli.slack.messages import send_notification_about_new_server
from dev_cli.settings.main import DOMAIN, EC2_NAME_TAG_PREFIX, DOMAIN_EMAIL, EC2_INSTANCE_USER

env.use_ssh_config = True


def get_hostname(name):
    return '{}.{}'.format(name, DOMAIN)


@task(name='list')
def list_servers():
    """- Finds all provisioned hosts"""
    with hide('running'):
        instances = filter_ec2_instances('{}*'.format(EC2_NAME_TAG_PREFIX))

        for instance in instances:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']

            host_tags = filter(lambda x: x['Key'] == 'Host', instance['Tags'])
            host = list(host_tags)[0]['Value'] if host_tags else ''
            formatted_host = green(host) if state == 'running' else red(host)

            print('{} ({}) - {}'.format(formatted_host, instance_id, state))


@task
def install_ssl(name):
    """- Configures letsencrypt certificate for specific server"""
    sudo('apt-get install -y nginx python-certbot-nginx')
    run('sudo certbot certonly --nginx -d {}.{} --renew-by-default --email {} --agree-tos -n'.format(
        name, DOMAIN, DOMAIN_EMAIL
    ))


@task
def update_subdomain_ip(name):
    ip_address = get_ec2_instance(name)['PublicIpAddress']

    print(
        yellow(
            'Creating DNS record {}.{} for IP: {} (waiting for propagation)'.format(name, DOMAIN, ip_address)
        )
    )

    create_subdomain(name, ip_address)


@task
def update_hostname(name):
    run('sudo bash -c "echo {} > /etc/hostname"'.format(get_hostname(name)))
    run('sudo hostname {}'.format(get_hostname(name)))


@task
def provision(name):
    """- Creates and provisions a new EC2 instance"""

    hostname = get_hostname(name)
    env.hosts = ['{}@{}'.format(EC2_INSTANCE_USER, hostname)]

    is_confirmed = confirm(
        red('You are provisioning dev server instance {}.\n'
            'If there is an instance already created for that name, '
            'DNS record will be replaced, but the old instance will continue running.\n'
            'If that\'s the case, make sure to terminate old instance.\n'
            'Do you want to continue?'.format(hostname)))

    if not is_confirmed:
        return

    print(yellow('Creating EC2 instance (be patient, that takes some time)'))
    create_ec2_instance(name)

    execute(update_subdomain_ip, name=name)

    print(yellow('Installing SSL certificate'))
    execute(install_ssl, name=name, hosts=env.hosts)

    print(yellow('Updating hostname'))
    execute(update_hostname, name=name, hosts=env.hosts)

    print(
        green('Provisioning has been completed. You can start deploying your code!')
    )

    send_notification_about_new_server(host=hostname)


@task
def start(name):
    """- Starts previously stopped instance"""
    print(yellow('Starting EC2 instance {}'.format(get_hostname(name))))
    start_ec2_instance(name)
    execute(update_subdomain_ip, name=name)


@task
def stop(name):
    """- Changes instance state to stopped"""
    print(yellow('Stopping EC2 instance {}'.format(get_hostname(name))))
    stop_ec2_instance(name)


@task
def reboot(name):
    """- First stops, then re-starts the instance"""
    execute(stop, name=name)
    execute(start, name=name)


@task
def terminate(name):
    """- Removes the AWS resources for a given name"""
    is_confirmed = confirm(
        red('EC2 instance {}.{} will be terminated. Do you want to continue?'.format(name, DOMAIN))
    )

    if not is_confirmed:
        return

    print(yellow('Terminating EC2 instance {}.{}'.format(name, DOMAIN)))
    terminate_ec2_instance(name)

