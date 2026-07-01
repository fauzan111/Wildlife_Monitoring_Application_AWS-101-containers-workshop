#!/usr/bin/env python3

import boto3

## Disable logging for Code Server ALB

client = boto3.client('elbv2')

# Get ALB ARN by name
response = client.describe_load_balancers(Names=['wildlife-alb-codeserver'])
alb_arn = response['LoadBalancers'][0]['LoadBalancerArn']

client.modify_load_balancer_attributes(
LoadBalancerArn=alb_arn,
Attributes=[
        {
        'Key': 'access_logs.s3.enabled',
        'Value': 'false'
        }
    ]
)

## Disable logging for Code Server CloudFront Distribution

client = boto3.client('cloudfront')

# Get current distribution config
response = client.get_distribution_config(Id='E9Z2VLT6OLCFR')
config = response['DistributionConfig']
etag = response['ETag']

# Disable logging
config['Logging']['Enabled'] = False

# Update distribution
client.update_distribution(
    Id='E9Z2VLT6OLCFR',
    DistributionConfig=config,
    IfMatch=etag
)

## Empty workshop S3 buckets

BUCKETS = [
    'aws102-ws-s3bucketartifact-v5jxytu8zyef',
    'aws102-ws-s3bucketgit-npdrdjql9fjx',
    'aws102-ws-s3bucketlogs-cf5beowjnbfw',
    'aws102-ws-s3bucketwildlife-kftpkarnijyv'
]

s3 = boto3.resource('s3')

for bucket_name in BUCKETS:
    try:
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.object_versions.delete()
        print(f"Deleted all objects from S3 bucket: {bucket_name}")
    except Exception as e:
        print(f"Error deleting objects from S3 bucket: {bucket_name}: {e}")


# Disable container insights for ECS cluster
ecs = boto3.client('ecs')

ecs.update_cluster(
    cluster='wildlife-ecs',
    settings=[
        {
            'name': 'containerInsights',
            'value': 'disabled'
        }
    ]
)

# Delete workshop CloudWatch log groups
log_groups = [
    '/aws/codebuild/wildlife-codebuildproject-terraform-build',
    '/aws/codepipeline/wildlife-pipeline',
    '/aws/ec2/wildlife-codeserver',
    '/aws/ecs/wildlife-alerts',
    '/aws/ecs/xray-daemon',
    '/aws/ecs/containerinsights/wildlife-ecs/performance',
    '/aws/ecs/service-connect/wildlife-app',
    '/aws/ecs/wildlife-dataapi',
    '/aws/ecs/wildlife-datadb',
    '/aws/ecs/wildlife-frontend',
    '/aws/ecs/wildlife-media',
    '/aws/lambda/wildlife-lambda-gps',
    '/aws/vpc/wildlife-flowlogs'
]

client = boto3.client('logs')

for log_group in log_groups:
    try:
        client.delete_log_group(logGroupName=log_group)
        print(f"Deleted: {log_group}")
    except:
        print(f"Failed: {log_group}")