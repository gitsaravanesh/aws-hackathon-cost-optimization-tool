import boto3

# Initialize AWS clients
ec2 = boto3.client('ec2')
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

# DynamoDB table
table = dynamodb.Table('BBI_Resource_Optimization')

def get_approved_resources(resource_type):
    """
    Fetch approved resources from DynamoDB based on resource type.
    :param resource_type: 'ec2' or 's3'
    :return: List of approved resource IDs
    """
    try:
        response = table.scan(
            ExpressionAttributeNames={"#status": "status"},
            FilterExpression="#status = :status",
            ExpressionAttributeValues={":status": "approved"}
        )
        print(f"Raw DynamoDB Response: {response}")
        
        resources = [
            item['resource-id'].split('/')[-1]
            for item in response['Items']
            if item.get('type-of-resource') == resource_type
        ]
        return resources
    except Exception as e:
        print(f"Error fetching approved {resource_type} resources: {e}")
        raise

def terminate_instance(instance_id):
    """
    Terminate an EC2 instance.
    """
    try:
        print(f"Terminating EC2 instance: {instance_id}")
        ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} terminated successfully.")
        
        # Update the status in DynamoDB
        response = table.scan(
            FilterExpression="contains(#resource_id, :resource_id)",
            ExpressionAttributeNames={"#resource_id": "resource-id"},
            ExpressionAttributeValues={":resource_id": instance_id}
        )
        for item in response.get('Items', []):
            table.update_item(
                Key={'resource-id': item['resource-id']},
                UpdateExpression="SET #status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": "deleted"}
            )
            print(f"Updated DynamoDB for resource-id: {item['resource-id']}")
        
    except Exception as e:
        print(f"Error terminating instance {instance_id}: {e}")
        raise

def move_s3_object_to_deep_archive(bucket_name, object_key):
    """
    Move an S3 object to Deep Archive.
    """
    try:
        print(f"Moving S3 object {object_key} in bucket {bucket_name} to Deep Archive")
        s3.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': object_key},
            Key=object_key,
            StorageClass='DEEP_ARCHIVE'
        )
        s3.delete_object(Bucket=bucket_name, Key=object_key)
        print(f"Object {object_key} moved to Deep Archive successfully.")
    except Exception as e:
        print(f"Error moving S3 object {object_key} to Deep Archive: {e}")
        raise

def lambda_handler(event, context):
    """
    Lambda handler function to manage EC2 and S3 resources.
    """
    try:
        # Process approved EC2 instances
        approved_instances = get_approved_resources('ec2')
        print(f"Approved EC2 Instances: {approved_instances}")
        for instance_id in approved_instances:
            terminate_instance(instance_id)

        # Process approved S3 objects
        approved_s3_objects = get_approved_resources('s3')
        print(f"Approved S3 Objects: {approved_s3_objects}")
        for s3_resource in approved_s3_objects:
            # Extract bucket name and object key from resource ID
            bucket_name, object_key = s3_resource.split('/', 1)
            move_s3_object_to_deep_archive(bucket_name, object_key)

    except Exception as e:
        print(f"Error in Lambda function: {e}")
        raise
