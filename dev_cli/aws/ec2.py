import boto3

from dev_cli.settings.main import AWS_DEFAULT_REGION, EC2_SECURITY_GROUPS, EC2_KEYPAIR_NAME, EC2_AMI_ID, \
    EC2_NAME_TAG_PREFIX, DOMAIN, EC2_INSTANCE_TYPE, EC2_IAM_PROFILE_NAME


def get_ec2_instance(name):
    ec2_client = boto3.client('ec2', region_name=AWS_DEFAULT_REGION)
    return ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Host',
                'Values': ['{}.{}'.format(name, DOMAIN)]
            }
        ]
    )['Reservations'][0]['Instances'][0]


def filter_ec2_instances(pattern):
    ec2_client = boto3.client('ec2', region_name=AWS_DEFAULT_REGION)
    found_reservations = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [pattern]
            }
        ]
    )['Reservations']

    return [reservation['Instances'][0] for reservation in found_reservations]


def get_ec2_waiter(waiter_name):
    ec2_client = boto3.client('ec2', region_name=AWS_DEFAULT_REGION)
    return ec2_client.get_waiter(waiter_name)


def get_instances(name):
    instance_info = get_ec2_instance(name)

    ec2 = boto3.resource('ec2', region_name=AWS_DEFAULT_REGION)
    return ec2.instances.filter(InstanceIds=[instance_info['InstanceId']])


def stop_ec2_instance(name):
    get_instances(name).stop()
    get_ec2_waiter('instance_stopped').wait(InstanceIds=[get_ec2_instance(name)['InstanceId']])


def start_ec2_instance(name):
    get_instances(name).start()
    get_ec2_waiter('instance_running').wait(InstanceIds=[get_ec2_instance(name)['InstanceId']])


def terminate_ec2_instance(name):
    get_instances(name).terminate()
    get_ec2_waiter('instance_terminated').wait(InstanceIds=[get_ec2_instance(name)['InstanceId']])


def create_ec2_instance(name):
    ec2 = boto3.resource('ec2', region_name=AWS_DEFAULT_REGION)

    ec2_instance = ec2.create_instances(
        InstanceType=EC2_INSTANCE_TYPE,
        KeyName=EC2_KEYPAIR_NAME,
        MinCount=1,
        MaxCount=1,
        Monitoring={
            'Enabled': False
        },
        # Volume is attached from the AMI
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'NoDevice': ''
            }
        ],
        ImageId=EC2_AMI_ID,
        SecurityGroups=EC2_SECURITY_GROUPS,
        IamInstanceProfile={
            'Name': EC2_IAM_PROFILE_NAME
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': '{}{}'.format(EC2_NAME_TAG_PREFIX, name)
                    },
                    {
                        'Key': 'Host',
                        'Value': '{}.{}'.format(name, DOMAIN)
                    }
                ]
            },
            {
                'ResourceType': 'volume',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': '{}{}'.format(EC2_NAME_TAG_PREFIX, name)
                    }
                ]
            },
        ],
    )[0]

    get_ec2_waiter('instance_running').wait(InstanceIds=[ec2_instance.id])

    return ec2_instance.id, get_ec2_instance(name)['PublicIpAddress']
