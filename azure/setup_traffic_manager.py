from azure.identity import InteractiveBrowserCredential
from azure.mgmt.trafficmanager import TrafficManagerManagementClient
from azure.mgmt.trafficmanager.models import (
    Profile, DnsConfig, MonitorConfig, Endpoint
)
import uuid

def create_traffic_manager_profile(traffic_manager_client, resource_group_name, profile_name, location):
    unique_label = f"{profile_name}-{uuid.uuid4().hex[:6]}"  # Generate a unique DNS label
    profile_params = Profile(
        location=location,
        traffic_routing_method='Performance',
        dns_config=DnsConfig(
            relative_name=unique_label,
            ttl=30
        ),
        monitor_config=MonitorConfig(
            protocol='HTTP',
            port=80,
            path='/'
        )
    )
    return traffic_manager_client.profiles.create_or_update(
        resource_group_name, profile_name, profile_params
    )

def create_traffic_manager_endpoint(traffic_manager_client, resource_group_name, profile_name, endpoint_name, target_resource_id):
    endpoint_params = Endpoint(
        name=endpoint_name,
        type='Microsoft.Network/trafficManagerProfiles/externalEndpoints',
        target_resource_id=target_resource_id,
        endpoint_status='Enabled',
        endpoint_location='global'
    )
    return traffic_manager_client.endpoints.create_or_update(
        resource_group_name, profile_name, endpoint_name, endpoint_params
    )

def main():
    # Replace with your Azure subscription ID and tenant ID
    subscription_id = '16d7b6cf-cfcd-466f-933a-7de50afb11f7'
    tenant_id = '9c33bd1d-9ba6-4240-a5fe-7549c7bbcb17'

    # Define resource group, location, and names
    resource_group_name = 'FangResourceGroup'
    location = 'global'
    profile_name = 'myTrafficManagerProfile'
    vm2_id = '/subscriptions/16d7b6cf-cfcd-466f-933a-7de50afb11f7/resourceGroups/FangResourceGroup/providers/Microsoft.Compute/virtualMachines/myVM2'
    vm3_id = '/subscriptions/16d7b6cf-cfcd-466f-933a-7de50afb11f7/resourceGroups/FangResourceGroup/providers/Microsoft.Compute/virtualMachines/myVM3'

    # Initialize credentials and client
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    traffic_manager_client = TrafficManagerManagementClient(credential, subscription_id)

    # Create Traffic Manager Profile
    profile = create_traffic_manager_profile(traffic_manager_client, resource_group_name, profile_name, location)
    print(f"Traffic Manager Profile created: {profile.id}")

    # Create Traffic Manager Endpoints
    endpoint_vm2 = create_traffic_manager_endpoint(traffic_manager_client, resource_group_name, profile_name, 'myVM2Endpoint', vm2_id)
    print(f"Traffic Manager Endpoint for myVM2 created: {endpoint_vm2.id}")

    endpoint_vm3 = create_traffic_manager_endpoint(traffic_manager_client, resource_group_name, profile_name, 'myVM3Endpoint', vm3_id)
    print(f"Traffic Manager Endpoint for myVM3 created: {endpoint_vm3.id}")

if __name__ == "__main__":
    main()