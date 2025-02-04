#create mutiple VMs in different locations
from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption

def create_resource_group(resource_client, resource_group_name, location):
    resource_client.resource_groups.create_or_update(resource_group_name, {'location': location})

def create_virtual_network(network_client, resource_group_name, location):
    vnet_params = {
        'location': location,
        'address_space': {'address_prefixes': ['10.0.0.0/16']}
    }
    return network_client.virtual_networks.begin_create_or_update(resource_group_name, f'myVNet_{location}', vnet_params).result()

def create_subnet(network_client, resource_group_name, location):
    subnet_params = {'address_prefix': '10.0.0.0/24'} #dynamic, if needs to be static, need to put the specific address. ex. {'address_prefix': '10.0.1.0/24'} 
    return network_client.subnets.begin_create_or_update(resource_group_name, f'myVNet_{location}', f'mySubnet_{location}', subnet_params).result()

def create_network_interface(network_client, resource_group_name, location, subnet_id, nic_name):
    nic_params = {
        'location': location,
        'ip_configurations': [{
            'name': 'myIPConfig',
            'subnet': {'id': subnet_id}
        }]
    }
    return network_client.network_interfaces.begin_create_or_update(resource_group_name, nic_name, nic_params).result()

def create_vm(compute_client, resource_group_name, location, vm_name, nic_id):
    vm_params = {
        'location': location,
        'hardware_profile': {'vm_size': 'Standard_DS1_v2'},
        'storage_profile': {
            'image_reference': {
                'publisher': 'Canonical',
                'offer': 'UbuntuServer',
                'sku': '18.04-LTS',
                'version': 'latest'
            },
            'os_disk': {
                'create_option': DiskCreateOption.from_image,
                'managed_disk': {'storage_account_type': 'Standard_LRS'}
            }
        },
        'os_profile': {
            'computer_name': vm_name,
            'admin_username': 'azureuser',
            'admin_password': 'Password1234!'
        },
        'network_profile': {
            'network_interfaces': [{'id': nic_id}]
        }
    }
    return compute_client.virtual_machines.begin_create_or_update(resource_group_name, vm_name, vm_params).result()

def main():
    # Replace with your Azure subscription ID and tenant ID
    subscription_id = '16d7b6cf-cfcd-466f-933a-7de50afb11f7'
    tenant_id = '9c33bd1d-9ba6-4240-a5fe-7549c7bbcb17'

    # Initialize credentials and clients
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    resource_client = ResourceManagementClient(credential, subscription_id)
    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    # Define resource group and VM details
    resource_group_name = 'FangResourceGroup'
    locations = ['eastus', 'westus']
    vm_names = ['myVM1', 'myVM2', 'myVM3', 'myVM4']

    # Create a resource group
    create_resource_group(resource_client, resource_group_name, locations[0])

    # Loop through the locations and VM names to create VMs
    for i, location in enumerate(locations):
        # Create a virtual network and subnet
        vnet_result = create_virtual_network(network_client, resource_group_name, location)
        subnet_result = create_subnet(network_client, resource_group_name, location)

        # Create two VMs in each location
        for j in range(2):
            vm_name = vm_names[i * 2 + j]
            nic_name = f'myNic_{location}_{i}_{j}'  # Ensure unique NIC name
            nic_result = create_network_interface(network_client, resource_group_name, location, subnet_result.id, nic_name)
            vm_result = create_vm(compute_client, resource_group_name, location, vm_name, nic_result.id)
            print(f"VM {vm_name} created successfully in {location}.")

if __name__ == "__main__":
    main()

