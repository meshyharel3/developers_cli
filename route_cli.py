import click
import boto3

@click.group()
def cli():
    """the best CLI for managing Route53."""
    pass

@click.command()
@click.option('--manage', type=click.Choice(['create', 'update', 'delete'], case_sensitive=False),
              help='Action to perform.')
@click.option('--type', type=click.Choice(['public', 'private'], case_sensitive=False),
              help='Access control for the hosted zone (only required for create action).')
@click.option('--name', help='Name of the DNS or hosted zone.')
@click.option('--hosted-zone-id', help='Hosted Zone ID for updating or deleting records (required for update/delete action).')
@click.option('--record-name', help='The DNS record name to update or delete (required for update/delete action).')
@click.option('--my-ip', help='The IP address to set for the A record (required for update action).')
def route53(manage, type, name, hosted_zone_id, record_name, my_ip):
    """Perform actions on Route53."""
    client = boto3.client('route53')
    
    if manage == "create":
        if not type or not name:
            click.echo("Error: --type and --name are required for the create action.")
            return

        VPC_ID = 'vpc-0148e740f898c298d'
      
        if type == 'private':
            response = client.create_hosted_zone(
                Name=name,
                VPC={
                    'VPCRegion': 'us-east-1',
                    'VPCId': VPC_ID
                },
                CallerReference=name,
                HostedZoneConfig={
                    'PrivateZone': True
                }
            )
        elif type == 'public':
            response = client.create_hosted_zone(
                Name=name,
                CallerReference=name,
                HostedZoneConfig={
                    'PrivateZone': False
                }
            )

        click.echo(f"Hosted Zone created: {response['HostedZone']['Id']}")

    elif manage == 'update':
        if not hosted_zone_id or not record_name or not my_ip:
            click.echo("Error: --hosted-zone-id, --record-name, and --my-ip are required for the update action.")
            return

        response = client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": record_name,
                            "Type": "A",
                            "TTL": 300,
                            "ResourceRecords": [
                                {
                                    "Value": my_ip
                                }
                            ],
                        }
                    }
                ]
            }
        )
        click.echo(f"Record set updated: {response['ChangeInfo']['Id']}")

    elif manage == 'delete':
        if not hosted_zone_id or not record_name:
            click.echo("Error: --hosted-zone-id and --record-name are required for the delete action.")
            return

        response = client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": record_name,
                            "Type": "A",
                            "TTL": 300
                        }
                    }
                ]
            }
        )
        click.echo(f"Record set deleted: {response['ChangeInfo']['Id']}")

cli.add_command(route53)

if __name__ == '__main__':
    cli()

