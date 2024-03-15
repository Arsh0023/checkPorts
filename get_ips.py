import boto3
import config

def get_public_ips(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)

    public_ips = []

    response = ec2.describe_instances()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if 'PublicIpAddress' in instance:
                public_ips.append(instance['PublicIpAddress'])

    return public_ips

if __name__ == "__main__":
    region_name = config.REGION  # Replace 'your_region_name' with the desired region name, e.g., 'us-west-1'

    public_ips = get_public_ips(region_name)
    print("Public IP addresses in region {}: {}".format(region_name, public_ips))