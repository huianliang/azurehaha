from azure.identity import InteractiveBrowserCredential
from azure.mgmt.network import NetworkManagementClient

def delete_load_balancer(network_client, resource_group_name, lb_name):
    # Delete the load balancer
    print(f"Deleting Load Balancer: {lb_name}")
    async_lb_delete = network_client.load_balancers.begin_delete(resource_group_name, lb_name)
    async_lb_delete.result()  # Wait for the operation to complete
    print(f"Load Balancer {lb_name} deleted successfully.")

def main():
    # Replace with your Azure subscription ID and tenant ID
    subscription_id = '16d7b6cf-cfcd-466f-933a-7de50afb11f7'
    tenant_id = '9c33bd1d-9ba6-4240-a5fe-7549c7bbcb17'

    # Define resource group and load balancer name
    resource_group_name = 'FangResourceGroup'
    lb_name = 'myLoadBalancer'

    # Initialize credentials and client
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    # Delete the load balancer
    delete_load_balancer(network_client, resource_group_name, lb_name)

if __name__ == "__main__":
    main()