import click
import boto3
from botocore.exceptions import ClientError


my_session = boto3.session.Session()
s3 = my_session.client('s3', region_name='us-east-1')


@click.group()
def cli():
    """A CLI for managing S3 buckets."""
    pass


@click.command()
@click.option('--action', type=click.Choice(['create', 'upload', 'list'],
                                            case_sensitive=False),
              required=True, help='Action to perform.')
@click.option('--access',
              type=click.Choice(['public', 'private'], case_sensitive=False),
              help='Access control for the bucket (only required for create action).')
@click.option('--bucketname', help='Name of the bucket.')
@click.option('--path',
              help='Path of the file to upload (only required for upload action).')
def s3manage(action, access, bucketname, path):
    if action == 'create':
        if not bucketname or not access:
            click.echo(
                "For the 'create' action, both --bucketname and --access are required.")
            return
    #   double check if the developer want to create public bucket
        if access == 'public':
            if not click.confirm(
                    f"Are you sure you want to create a public bucket '{bucketname}'?",
                    default=False):
                click.echo("yay! bucket created! now its your time to upload files.")
                return
        #  put the bucket in the default region
        # -but he can create on in another
        try:
            if my_session.region_name == 'us-east-1':
                s3.create_bucket(
                        ACL=access,
                        Bucket=bucketname
                )
            else:
                click.echo("error! please specify the right region!")

            # tag the bucket
            s3.put_bucket_tagging(
                    Bucket=bucketname,
                    Tagging={
                        'TagSet': [
                            {'Key': 'session', 'Value': 'cli'},
                            {'Key': 'name', 'Value': 'Meshy'}
                        ]
                    }
            )
            click.echo(
                f"Bucket '{bucketname}' tagged with 'session:cli' and 'name:Meshy'.")

        except ClientError as e:
            click.echo(f"Error creating bucket: {e}")

    elif action == 'upload':
        if not bucketname or not path:
            click.echo(
                "For the 'upload' action, both --bucketname and --path are required.")
            return

        try:
            s3.upload_file(path, bucketname)
            click.echo(f"File '{path}' uploaded to bucket '{bucketname}'.")

        except FileNotFoundError:
            click.echo(f"File '{path}' not found.")
        except ClientError as e:
            click.echo(f"Error uploading file: {e}")

    elif action == 'list':
        if not bucketname:
            click.echo("For the 'list' action, --bucketname is required.")
            return

        try:
            response = s3.list_objects_v2(Bucket=bucketname)
            if 'Contents' in response:
                click.echo(f"Contents of bucket '{bucketname}':")
                for obj in response['Contents']:
                    click.echo(f" - {obj['Key']}")
            else:
                click.echo(
                    f"Bucket '{bucketname}' is empty or does not exist.")

        except ClientError as e:
            click.echo(f"Error listing bucket contents: {e}")


cli.add_command(s3manage)

if __name__ == '__main__':
    cli()

