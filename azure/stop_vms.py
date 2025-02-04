from azure.identity import InteractiveBrowserCredential
from azure.mgmt.compute import ComputeManagementClient

def stop_vms(subscription_id, tenant_id, resource_group_name, vm_names):
    # Initialize credentials and clients
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Stop each VM
    for vm_name in vm_names:
        print(f"Stopping VM: {vm_name}")
        async_vm_stop = compute_client.virtual_machines.begin_power_off(resource_group_name, vm_name)
        async_vm_stop.result()  # Wait for the operation to complete
        print(f"VM {vm_name} stopped successfully.")

def deallocate_vms(subscription_id, tenant_id, resource_group_name, vm_names):
    # Initialize credentials and clients
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Deallocate each VM
    for vm_name in vm_names:
        print(f"Deallocating VM: {vm_name}")
        async_vm_deallocate = compute_client.virtual_machines.begin_deallocate(resource_group_name, vm_name)
        async_vm_deallocate.result()  # Wait for the operation to complete
        print(f"VM {vm_name} deallocated successfully.")

def main():
    # Replace with your Azure subscription ID and tenant ID
    subscription_id = '16d7b6cf-cfcd-466f-933a-7de50afb11f7'
    tenant_id = '9c33bd1d-9ba6-4240-a5fe-7549c7bbcb17'

    # Define resource group and VM names
    resource_group_name = 'FangResourceGroup'
    vm_names = ['myVM1', 'myVM2', 'myVM3', 'myVM4']

    # Deallocate the VMs
    deallocate_vms(subscription_id, tenant_id, resource_group_name, vm_names)

if __name__ == "__main__":
    main()