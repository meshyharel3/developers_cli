import click
import boto3

# Initialize boto3 EC2 client
ec2 = boto3.client('ec2', region_name='us-east-1')

# Define a permanent subnet ID here
SUBNET_ID = 'subnet-02fc4b50fae2e8f12'

def get_tagged_instances():
    """Fetch instances created by CLI based on a specific tag."""
    response = ec2.describe_instances(
        Filters=[{'Name': 'tag:CreatedByCLI', 'Values': ['true']}]
    )
    instances = []
    running_count = 0
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)
            if instance['State']['Name'] == 'running':
                running_count += 1
            return instances, running_count

@click.group()
def cli():
    """Welcome to the best CLI tool to manage your AWS instances."""
    pass

@click.command()
@click.option('--action',
              type=click.Choice(['create', 'manage', 'list']),
              prompt='Action (create, manage, list)',
              help='The action to perform.')
@click.option('--type',
              type=click.Choice(['t3.nano', 't4g.nano'], case_sensitive=False),
              help='Type of EC2 instance (required for create action).')
@click.option('--ami',
              type=click.Choice(['ubuntu', 'linux'], case_sensitive=False),
              help='The type of AMI to use (required for create action).')
@click.option('--count', default=1, type=int,
              help='Number of EC2 instances to create.')
@click.option('--instance_state',
              type=click.Choice(['start', 'stop', 'terminate']),
              help='Action to manage EC2 instances (required for manage action).')
@click.argument('instance_ids', nargs=-1)
@click.option('--name', default='MyInstance',
              help='Name to assign to the EC2 instance .')
def instance(action,type,name, ami, count, instance_state, instance_ids):
    """Manage EC2 instances based on the specified action."""
    if action == 'create':
        if not ami or not type:
            click.echo("The --ami and --type options are required for the create action.")
            return

        # counting the running ec2
        existing_instances, running_count = get_tagged_instances()
        if running_count + count > 2:
            click.echo("Sorry! You can create a maximum of 2 running EC2 instances.")
            return

        # define the images
        ami_ids = {
            'ubuntu': 'ami-0e86e20dae9224db8',
            'linux': 'ami-0182f373e66f89c85'
        }

        image_id = ami_ids[ami]
        response = ec2.run_instances(
            ImageId=image_id,
            InstanceType=type,
            MinCount=1,
            MaxCount=count,
            NetworkInterfaces=[{
                'SubnetId': SUBNET_ID,
                'DeviceIndex': 0
            }],
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'CreatedByCLI', 'Value': 'true'},
                         {'Key': 'Name', 'Value': name}
                         ]

            }]
        )

        instance_ids = [instance['InstanceId'] for instance in response['Instances']]
        click.echo(f"Creating EC2 instances: {', '.join(instance_ids)}")

    elif action == 'manage':
        if not instance_state or not instance_ids:
            click.echo("You must provide at least one instance ID and an action (start, stop, or terminate) for the manage action.")
            return

        if instance_state == 'start':
            ec2.start_instances(InstanceIds=list(instance_ids))
            click.echo(f"Starting EC2 instances: {', '.join(instance_ids)}")

        elif instance_state == 'stop':
            ec2.stop_instances(InstanceIds=list(instance_ids))
            click.echo(f"Stopping EC2 instances: {', '.join(instance_ids)}")

        elif instance_state == 'terminate':
            ec2.terminate_instances(InstanceIds=list(instance_ids))
            click.echo(f"Terminating EC2 instances: {', '.join(instance_ids)}")

    elif action == 'list':
        response = ec2.describe_instances(
            Filters=[{'Name': 'tag:CreatedByCLI', 'Values': ['true']}]
        )

        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'PublicIpAddress': instance.get('PublicIpAddress', 'N/A'),
                    'State': instance['State']['Name']
                })

        if instances:
            click.echo(f"{'Instance ID':<20} {'Instance Type':<20} {'Public IP Address':<20} {'State':<10}")
            click.echo('-' * 70)
            for instance in instances:
                click.echo(f"{instance['InstanceId']:<20} {instance['InstanceType']:<20} {instance['PublicIpAddress']:<20} {instance['State']:<10}")
        else:
            click.echo("No running EC2 instances found.")

cli.add_command(instance)

if __name__ == '__main__':
    cli()
