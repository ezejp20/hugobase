#!/bin/python3

from aws_helpers.s3 import S3Bucket, S3Client
import argparse
from boto3.session import Session
import json
import os
import subprocess

BUCKET_NAME = 'ellen-zehra.me'
BUCKET_REGION = 'eu-west-1'

def create_parser():
    """Create parser object used for defining all options for locust-nest.

    Returns:
        ArgumentParser: ArgumentParser object used in *parse_options*.
    """

    # Initialize
    parser = argparse.ArgumentParser(usage="python deploy [options]")

    parser.add_argument(
        '-d','--hugo-dir',
        dest='hugo_dir',
        default=None,
        help="Directory containing config.toml."
    )

    parser.add_argument(
        '--no-prompt',
        action='store_false',
        dest='prompt',
        default=True,
        help="Prompt before each stage."
    )

    parser.add_argument(
        '--no-mock-media',
        action='store_false',
        dest='mock_media',
        default=True,
        help="Touch media files from s3 in local hugo 'img/photos'."
    )

    parser.add_argument(
        '--no-rebuild',
        action='store_false',
        dest='rebuild',
        default=True,
        help="Rebuild local website files using Hugo and *baseurl*."
    )

    parser.add_argument(
        '--baseurl',
        action='store',
        dest='baseurl',
        default=None,
        help="baseURL for hugo generation (url of website)."
    )

    parser.add_argument(
        '--no-delete-local',
        action='store_false',
        dest='delete_local',
        default=True,
        help="Delete local website files before rebuild."
    )

    parser.add_argument(
        '--no-upload',
        action='store_false',
        dest='upload',
        default=True,
        help="Upload website to s3."
    )

    parser.add_argument(
        '--no-delete-s3',
        action='store_false',
        dest='delete_s3',
        default=True,
        help="Delete s3 website files before upload."
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        dest='debug',
        default=False,
        help="Print debug messages."
    )
    return parser


def touch(fname):
    """Touch files."""
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    try:
        with open(fname, 'a') as f:
            f.write('')
        return True
    except IsADirectoryError:
        return False


def mock_media_files(bucket, prefix='img/photos/'):
    """For each file in dir, create a fake image with the same name.

    Keyword Arguments:
        prefix {str} -- folder to search (default: {'img/photos/'})

    Returns:
        list --  Return a list of successful touches.
    """

    photos = [x.key for x in bucket.get_files(prefix=prefix)]
    successful = []
    for photo in photos:
        dummy_file_name = photo.replace('img', 'static/img')
        if touch(dummy_file_name):
            print('Touching "{}"'.format(dummy_file_name))
            successful.append(dummy_file_name)
    return successful


def deploy(
        prompt=True,
        hugo_dir=None,
        rebuild=True,
        mock_media=True,
        bucket_name=None,
        bucket_region=None,
        baseURL=None,
        delete_local=True,
        upload=True,
        delete_s3=True,
        debug=True):

    def display_prompt(message, prompt=prompt):
        if not (debug or prompt):
            return True
        cont = ' [y/n]?'
        ys = ['Yes', 'yes', 'y','Y']
        print('{}{}'.format(message, cont if prompt else ''))
        if prompt:
            ans = input()
            if ans in ys:
                return True
            else:
                return False
        return True

    if hugo_dir:
        d = os.path.realpath(hugo_dir)
        display_prompt('Changing dir to {}'.format(d))
        os.chdir(os.path.realpath(d))
    elif debug:
        print('Using current working directory.')

    bucket = S3Bucket(BUCKET_NAME, BUCKET_REGION)
    # Rebuild hugo files
    if rebuild and display_prompt('Rebuilding static hugo files.'):
        if delete_local and display_prompt('Deleting previous build_dir "public/".'):
            # Remove public/
            display_prompt(
                subprocess.check_output(
                    [
                        'rm', 
                        '-rf{}'.format('v' if prompt else ''),
                        'public/'
                    ]).decode('utf-8'), prompt=False)

            display_prompt('Build dir deleted.', prompt=False)
            # Mock media files
            if mock_media and display_prompt('Mocking images from s3.'):
                mock_media_files(bucket)
                display_prompt('Images mocked.', prompt=False)

        # Run hugo
        if display_prompt('Generating static hugo site in "public/"'):
            command = ['hugo', '-F']
            if baseURL:
                command.append('--baseURL={}'.format(baseURL))
            out = subprocess.check_output(command).decode('utf-8') #all that is technically needed...
            print('{}'.format(out))
            if display_prompt('Deleting mocked S3 files in public/img/photos/*'):
                display_prompt(
                    subprocess.check_output(
                        [
                            'rm', 
                            '-rfv',
                            'public/img/photos'
                        ]).decode('utf-8'), prompt=False)

    # Get a list of all website files that have changed since rebuild
    changed_files = subprocess.check_output(['git', 'diff', '--name-only']).decode('utf-8').splitlines()
    removed = [x[7:] if x.startswith('public/') else None for x in changed_files]
    aws_changed_files = [x for x in removed if x is not None]
    # Delete s3 website files
    if delete_s3 and display_prompt('Deleting all files on s3 except "img/photos/*".'):
        # Delete all files EXCEPT img/photos/
        for f in aws_changed_files:
            print(f)
            bucket.delete_files(prefix=f,mock=True)
    # Upload to s3
    if upload and display_prompt('Uploading all files in "/public/*" except "/public/img/photos/*".'):
        # upload all files in public
        for f in aws_changed_files:
            bucket.upload_file(local_file='public/{}'.format(f), s3_path=f, mock=True)
            # upload_file(local_file='public/{}'.format(f), target_file=f, bucket_name=bucket_name, bucket_region=bucket_region, content_type='text/html', acl='public-read', mock=True)

    print('Deploy complete.')
    return


if __name__=="__main__":

    parser = create_parser()
    deploy_opts = parser.parse_args()
    print('OK! Let\'s go!')
    deploy(
        prompt        = deploy_opts.prompt,
        hugo_dir      = deploy_opts.hugo_dir,
        rebuild       = deploy_opts.rebuild,
        mock_media    = deploy_opts.mock_media,
        bucket_name   = BUCKET_NAME,
        bucket_region = BUCKET_REGION,
        baseURL       = deploy_opts.baseurl,
        delete_local  = deploy_opts.delete_local,
        upload        = deploy_opts.upload,
        delete_s3     = deploy_opts.delete_s3,
        debug         = deploy_opts.debug
    )
