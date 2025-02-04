from azure.identity import InteractiveBrowserCredential
from azure.mgmt.compute import ComputeManagementClient

def restart_vm(subscription_id, tenant_id, resource_group_name, vm_names):
    # Initialize credentials and clients
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Restart each VM
    for vm_name in vm_names:
        print(f"Restarting VM: {vm_name}")
        async_vm_restart = compute_client.virtual_machines.begin_restart(resource_group_name, vm_name)
        async_vm_restart.result()  # Wait for the operation to complete
        print(f"VM {vm_name} restarted successfully.")

def start_vm(subscription_id, tenant_id, resource_group_name, vm_names):
    # Initialize credentials and clients
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Start each VM
    for vm_name in vm_names:
        print(f"Starting VM: {vm_name}")
        async_vm_start = compute_client.virtual_machines.begin_start(resource_group_name, vm_name)
        async_vm_start.result()  # Wait for the operation to complete
        print(f"VM {vm_name} started successfully.")

def main():
    # Replace with your Azure subscription ID and tenant ID
    subscription_id = '16d7b6cf-cfcd-466f-933a-7de50afb11f7'
    tenant_id = '9c33bd1d-9ba6-4240-a5fe-7549c7bbcb17'

    # Define resource group and VM names
    resource_group_name = 'FangResourceGroup'
    vm_names = ['myVM2', 'myVM3', 'myVM4']

    # Start the VMs
    start_vm(subscription_id, tenant_id, resource_group_name, vm_names)

if __name__ == "__main__":
    main()