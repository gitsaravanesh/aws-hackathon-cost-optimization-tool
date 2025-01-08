import boto3
import json

# Initialize EC2 client for ap-south-1 region
ec2_client = boto3.client('ec2', region_name='ap-south-1')
pricing_client = boto3.client('pricing', region_name='us-east-1')  # Pricing API is only available in us-east-1

# Lambda function handler
def lambda_handler(event, context):
    try:
        # Get all running instances in ap-south-1
        response = ec2_client.describe_instances(Filters=[
            {"Name": "instance-state-name", "Values": ["running"]}
        ])

        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                region = instance['Placement']['AvailabilityZone'][:-1]  # Remove AZ letter (e.g., "ap-south-1a" -> "ap-south-1")

                # Get pricing details
                cost = get_instance_pricing(instance_type, region)
                if cost is not None:
                    instances.append({
                        "instance_id": instance_id,
                        "instance_type": instance_type,
                        "region": region,
                        "estimated_cost": cost
                    })

        if not instances:
            return {
                "statusCode": 404,
                "body": "No running instances found or no pricing details available."
            }

        return {
            "statusCode": 200,
            "body": instances
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }


def get_instance_pricing(instance_type, region):
    try:
        # Query pricing information
        response = pricing_client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
                {"Type": "TERM_MATCH", "Field": "location", "Value": get_region_name(region)},
                {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
                {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
                {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"}
            ]
        )

        # Parse pricing data
        for price_item in response['PriceList']:
            price_data = json.loads(price_item)
            terms = price_data.get("terms", {}).get("OnDemand", {})
            for _, term in terms.items():
                price_dimensions = term.get("priceDimensions", {})
                for _, dimension in price_dimensions.items():
                    return float(dimension['pricePerUnit']['USD'])

        return None

    except Exception as e:
        print(f"Error in get_instance_pricing: {str(e)}")
        return None


def get_region_name(region_code):
    region_names = {
        "us-east-1": "US East (N. Virginia)",
        "us-west-1": "US West (N. California)",
        "us-west-2": "US West (Oregon)",
        "eu-west-1": "EU (Ireland)",
        "eu-central-1": "EU (Frankfurt)",
        "ap-south-1": "Asia Pacific (Mumbai)",
        "ap-northeast-1": "Asia Pacific (Tokyo)",
        "ap-southeast-1": "Asia Pacific (Singapore)",
        "ap-southeast-2": "Asia Pacific (Sydney)"
    }
    return region_names.get(region_code, "Unknown Region")
