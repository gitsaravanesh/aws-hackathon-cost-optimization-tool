import boto3
import time
from datetime import datetime, timedelta

# DynamoDB table name
TABLE_NAME = 'BBI_Resource_Optimization'

# Helper function to fetch AWS Account ID using STS
def get_account_id():
    sts_client = boto3.client('sts')
    return sts_client.get_caller_identity()["Account"]

# Fetch running EC2 instances and generate their ARNs
def get_running_ec2_instances():
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    instances = []
    account_id = get_account_id()  # Fetch AWS Account ID

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            arn = f"arn:aws:ec2:{ec2_client.meta.region_name}:{account_id}:instance/{instance_id}"  # Use account_id
            instances.append({'InstanceId': instance_id, 'InstanceArn': arn})

    return instances

# Fetch CPU utilization for an EC2 instance
def get_cpu_utilization(instance_id, region):
    cloudwatch = boto3.client('cloudwatch', region_name=region)

    # Get CPU Utilization metric from CloudWatch
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=5)

    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average']
    )

    if response['Datapoints']:
        # Return the average CPU utilization if data is available
        return response['Datapoints'][0]['Average']
    else:
        return None  # No data points available

# Insert data into DynamoDB
def insert_into_dynamodb(instance_arn, unused_time, status, user_action, cost_optimized,type_of_resource):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    timestamp = int(time.time())

    table.put_item(
        Item={
            'resource-id': instance_arn,
            'unused-time': unused_time,
            'status': status,
            'user-action': user_action,
            'last-inserted': timestamp,
            'last-updated': timestamp,
            'cost-optimized': cost_optimized,
            'type-of-resource': type_of_resource
        }
    )

# Main function to process EC2 instances
def main():
    region = boto3.session.Session().region_name  # Get the Lambda's region
    ec2_instances = get_running_ec2_instances()

    for instance in ec2_instances:
        instance_id = instance['InstanceId']
        instance_arn = instance['InstanceArn']

        # Get CPU utilization
        cpu_utilization = get_cpu_utilization(instance_id, region)
        if cpu_utilization is None:
            print(f"No CPU data available for instance {instance_id}. Skipping.")
            continue

        print(f"Instance {instance_id} - CPU Utilization: {cpu_utilization}%")

        # Check if CPU utilization is below 2% for 5 minutes
        if cpu_utilization < 50:
            unused_time = 600  # Assuming active for 10 minutes
            status = 'pending'
            user_action = 'delete'  # Default action
            cost_optimized = 'false'
            type_of_resource = 'ec2'

            # Insert into DynamoDB
            insert_into_dynamodb(instance_arn, unused_time, status, user_action, cost_optimized,type_of_resource)
            print(f"Data inserted into DynamoDB for instance {instance_id}.")
        else:
            print(f"Instance {instance_id} does not meet the CPU threshold. Skipping.")

# AWS Lambda handler function
def lambda_handler(event, context):
    try:
        main()
        return {
            'statusCode': 200,
            'body': 'EC2 Monitoring Function executed successfully.'
        }
    except Exception as e:
        print(f"Error: {e}")
        raise e
