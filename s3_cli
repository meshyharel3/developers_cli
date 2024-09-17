import click
import boto3
from botocore.exceptions import ClientError


my_session = boto3.session.Session()
s3 = my_session.client('s3')


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
@click.option('--bucket_name', help='Name of the bucket.')
@click.option('--path',
              help='Path of the file to upload (only required for upload action).')
def s3_manage(action, access, bucket_name, path):
    if action == 'create':
        if not bucket_name or not access:
            click.echo(
                "For the 'create' action, both --bucket_name and --access are required.")
            return
    #   double check if the developer want to create public bucket
        if access == 'public':
            if not click.confirm(
                    f"Are you sure you want to create a public bucket '{bucket_name}'?",
                    default=False):
                click.echo("yay! bucket created! now its your time to upload files.")
                return
        #  put the bucket in the default region 
        #  but he can create on in another 
        try:
            if my_session.region_name == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={
                            'LocationConstraint': my_session.region_name}
                )

            # tag the bucket
            s3.put_bucket_tagging(
                    Bucket=bucket_name,
                    Tagging={
                        'TagSet': [
                            {'Key': 'session', 'Value': 'cli'},
                            {'Key': 'name', 'Value': 'Meshy'}
                        ]
                    }
            )
            click.echo(
                f"Bucket '{bucket_name}' tagged with 'session:cli' and 'name:Meshy'.")

            if access == 'public':
                s3.put_bucket_acl(Bucket=bucket_name, ACL='public-read')
                click.echo(
                    f"Bucket '{bucket_name}' created with public access.")
            else:
                click.echo(
                    f"Bucket '{bucket_name}' created with private access.")

        except ClientError as e:
            click.echo(f"Error creating bucket: {e}")

    elif action == 'upload':
        if not bucket_name or not path:
            click.echo(
                "For the 'upload' action, both --bucket_name and --path are required.")
            return

        try:
            s3.upload_file(path, bucket_name, path)
            click.echo(f"File '{path}' uploaded to bucket '{bucket_name}'.")

        except FileNotFoundError:
            click.echo(f"File '{path}' not found.")
        except ClientError as e:
            click.echo(f"Error uploading file: {e}")

    elif action == 'list':
        if not bucket_name:
            click.echo("For the 'list' action, --bucket_name is required.")
            return

        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                click.echo(f"Contents of bucket '{bucket_name}':")
                for obj in response['Contents']:
                    click.echo(f" - {obj['Key']}")
            else:
                click.echo(
                    f"Bucket '{bucket_name}' is empty or does not exist.")

        except ClientError as e:
            click.echo(f"Error listing bucket contents: {e}")


cli.add_command(s3_manage)

if __name__ == '__main__':
    cli()
