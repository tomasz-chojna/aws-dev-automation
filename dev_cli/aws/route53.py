import boto3

from dev_cli.settings.main import DOMAIN


def create_subdomain(name, ip_address):
    route53 = boto3.client('route53')
    hosted_zone = route53.list_hosted_zones_by_name(DNSName=DOMAIN)['HostedZones'][0]

    subdomain = route53.change_resource_record_sets(
        HostedZoneId=hosted_zone['Id'],
        ChangeBatch={
            'Comment': 'Dev environment - {}'.format(name),
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': '{}.{}'.format(name, DOMAIN),
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': ip_address
                            },
                        ],
                    }
                },
            ]
        }
    )

    waiter = route53.get_waiter('resource_record_sets_changed')
    waiter.wait(Id=subdomain['ChangeInfo']['Id'])

    return subdomain
