from azure.identity import InteractiveBrowserCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute.models import (
    HardwareProfile, NetworkProfile, NetworkInterfaceReference, OSProfile, StorageProfile, ImageReference, OSDisk, DiskCreateOptionTypes
)
from azure.mgmt.network.models import (
    NetworkSecurityGroup, SecurityRule, VirtualNetwork, Subnet, PublicIPAddress, NetworkInterface, IPConfiguration, PublicIPAddressSku
)

def create_resource_group(resource_client, resource_group_name, location):
    resource_group_params = {'location': location}
    return resource_client.resource_groups.create_or_update(resource_group_name, resource_group_params)

def create_virtual_network(network_client, resource_group_name, vnet_name, location):
    vnet_params = VirtualNetwork(
        location=location,
        address_space={'address_prefixes': ['10.0.0.0/16']}
    )
    return network_client.virtual_networks.begin_create_or_update(resource_group_name, vnet_name, vnet_params).result()

def create_subnet(network_client, resource_group_name, vnet_name, subnet_name):
    subnet_params = Subnet(address_prefix='10.0.0.0/24')
    return network_client.subnets.begin_create_or_update(resource_group_name, vnet_name, subnet_name, subnet_params).result()

def create_public_ip(network_client, resource_group_name, public_ip_name, location):
    public_ip_params = PublicIPAddress(
        location=location,
        public_ip_allocation_method='Static',  # Use 'Static' allocation method for Standard SKU
        sku=PublicIPAddressSku(name='Standard')  # Use 'Standard' SKU
    )
    return network_client.public_ip_addresses.begin_create_or_update(resource_group_name, public_ip_name, public_ip_params).result()

def create_network_interface(network_client, resource_group_name, nic_name, location, subnet_id, public_ip_id):
    ip_config = IPConfiguration(
        name=f'{nic_name}_ip_config',
        subnet={'id': subnet_id},
        public_ip_address={'id': public_ip_id}
    )
    nic_params = NetworkInterface(
        location=location,
        ip_configurations=[ip_config]
    )
    return network_client.network_interfaces.begin_create_or_update(resource_group_name, nic_name, nic_params).result()

def create_windows_vm(compute_client, resource_group_name, vm_name, location, nic_id):
    vm_params = {
        'location': location,
        'hardware_profile': HardwareProfile(vm_size='Standard_DS1_v2'),
        'storage_profile': StorageProfile(
            image_reference=ImageReference(
                publisher='MicrosoftWindowsServer',
                offer='WindowsServer',
                sku='2019-Datacenter',
                version='latest'
            ),
            os_disk=OSDisk(
                name=f'{vm_name}_os_disk',
                caching='ReadWrite',
                create_option=DiskCreateOptionTypes.from_image,
                managed_disk={'storage_account_type': 'Standard_LRS'}
            )
        ),
        'os_profile': OSProfile(
            computer_name=vm_name,
            admin_username='azureuser',
            admin_password='Password1234!'  # Replace with a secure password
        ),
        'network_profile': NetworkProfile(
            network_interfaces=[NetworkInterfaceReference(id=nic_id)]
        )
    }
    return compute_client.virtual_machines.begin_create_or_update(resource_group_name, vm_name, vm_params).result()

def main():
    # Replace with your Azure subscription ID and tenant ID
    subscription_id = '16d7b6cf-cfcd-466f-933a-7de50afb11f7'
    tenant_id = '9c33bd1d-9ba6-4240-a5fe-7549c7bbcb17'

    # Define resource group, location, and names
    resource_group_name = 'FangResourceGroup'
    location = 'eastus'
    vnet_name = 'myVNet'
    subnet_name = 'mySubnet'
    public_ip_name = 'myPublicIP'
    nic_name = 'myNIC'
    vm_name = 'myWindowsVM'

    # Initialize credentials and clients
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    resource_client = ResourceManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Create Resource Group
    create_resource_group(resource_client, resource_group_name, location)

    # Create Virtual Network
    vnet = create_virtual_network(network_client, resource_group_name, vnet_name, location)
    print(f"Virtual Network created: {vnet.id}")

    # Create Subnet
    subnet = create_subnet(network_client, resource_group_name, vnet_name, subnet_name)
    print(f"Subnet created: {subnet.id}")

    # Create Public IP
    public_ip = create_public_ip(network_client, resource_group_name, public_ip_name, location)
    print(f"Public IP created: {public_ip.id}")

    # Create Network Interface
    nic = create_network_interface(network_client, resource_group_name, nic_name, location, subnet.id, public_ip.id)
    print(f"Network Interface created: {nic.id}")

    # Create Windows VM
    vm = create_windows_vm(compute_client, resource_group_name, vm_name, location, nic.id)
    print(f"Windows VM created: {vm.id}")

if __name__ == "__main__":
    main()