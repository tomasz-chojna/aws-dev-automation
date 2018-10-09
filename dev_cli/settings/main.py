import os


def get_env_variable(name):
    value = os.environ.get(name)
    if value is None:
        raise Exception('{} env variable is not configured'.format(value))
    return value


AWS_DEFAULT_REGION = get_env_variable('AWS_DEFAULT_REGION')

EC2_KEYPAIR_NAME = get_env_variable('EC2_KEYPAIR_NAME')
EC2_INSTANCE_TYPE = get_env_variable('EC2_INSTANCE_TYPE')
EC2_INSTANCE_USER = get_env_variable('EC2_INSTANCE_USER')
EC2_AMI_ID = get_env_variable('EC2_AMI_ID')
EC2_NAME_TAG_PREFIX = get_env_variable('EC2_NAME_TAG_PREFIX')
EC2_SECURITY_GROUPS = get_env_variable('EC2_SECURITY_GROUPS').split(',')
EC2_IAM_PROFILE_NAME = get_env_variable('EC2_IAM_PROFILE_NAME')

DOMAIN = get_env_variable('DOMAIN')
DOMAIN_EMAIL = get_env_variable('DOMAIN_EMAIL')

SLACK_WEBHOOK_URL = get_env_variable('SLACK_WEBHOOK_URL')

