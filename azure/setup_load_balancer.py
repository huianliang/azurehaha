from azure.identity import InteractiveBrowserCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network.models import PublicIPAddress, LoadBalancer, Probe, LoadBalancingRule, BackendAddressPool, FrontendIPConfiguration

def create_public_ip(network_client, resource_group_name, location, public_ip_name):
    public_ip_params = PublicIPAddress(
        location=location,
        public_ip_allocation_method='Static',
        sku={'name': 'Standard'}
    )
    return network_client.public_ip_addresses.begin_create_or_update(
        resource_group_name, public_ip_name, public_ip_params).result()

def create_load_balancer(network_client, resource_group_name, location, lb_name, public_ip_id):
    frontend_ip_config = FrontendIPConfiguration(
        name=f'{lb_name}_frontend',
        public_ip_address={'id': public_ip_id}
    )
    lb_params = LoadBalancer(
        location=location,
        sku={'name': 'Standard'},
        frontend_ip_configurations=[frontend_ip_config]
    )
    return network_client.load_balancers.begin_create_or_update(
        resource_group_name, lb_name, lb_params).result()

def create_backend_pool(network_client, resource_group_name, lb_name, backend_pool_name):
    backend_pool_params = BackendAddressPool(name=backend_pool_name)
    return network_client.load_balancer_backend_address_pools.begin_create_or_update(
        resource_group_name, lb_name, backend_pool_name, backend_pool_params).result()

def create_health_probe(network_client, resource_group_name, lb_name, probe_name):
    probe_params = Probe(
        name=probe_name,
        protocol='Http',
        port=80,
        interval_in_seconds=15,
        number_of_probes=2,
        request_path='/'
    )
    lb = network_client.load_balancers.get(resource_group_name, lb_name)
    lb.probes.append(probe_params)
    return network_client.load_balancers.begin_create_or_update(resource_group_name, lb_name, lb).result().probes[-1]

def create_lb_rule(network_client, resource_group_name, lb_name, rule_name, frontend_ip_config_id, backend_pool_id, probe_id):
    lb_rule_params = LoadBalancingRule(
        name=rule_name,
        protocol='Tcp',
        frontend_port=80,
        backend_port=80,
        idle_timeout_in_minutes=4,
        enable_floating_ip=False,
        load_distribution='Default',
        frontend_ip_configuration={'id': frontend_ip_config_id},
        backend_address_pool={'id': backend_pool_id},
        probe={'id': probe_id}
    )
    lb = network_client.load_balancers.get(resource_group_name, lb_name)
    lb.load_balancing_rules.append(lb_rule_params)
    return network_client.load_balancers.begin_create_or_update(resource_group_name, lb_name, lb).result().load_balancing_rules[-1]

def associate_nic_with_lb(network_client, resource_group_name, nic_name, backend_pool_id):
    nic = network_client.network_interfaces.get(resource_group_name, nic_name)
    nic.ip_configurations[0].load_balancer_backend_address_pools = [{'id': backend_pool_id}]
    network_client.network_interfaces.begin_create_or_update(resource_group_name, nic_name, nic).result()

def main():
    # Replace with your Azure subscription ID and tenant ID
    subscription_id = '16d7b6cf-cfcd-466f-933a-7de50afb11f7'
    tenant_id = '9c33bd1d-9ba6-4240-a5fe-7549c7bbcb17'

    # Define resource group, location, and names
    resource_group_name = 'FangResourceGroup'
    location = 'eastus'
    public_ip_name = 'myPublicIP'
    lb_name = 'myLoadBalancer'
    backend_pool_name = 'myBackendPool'
    probe_name = 'myHealthProbe'
    rule_name = 'myLoadBalancingRule'
    vm_nics = ['myNic_eastus_0_1', 'myNic_westus_1_0', 'myNic_westus_1_1']  # NICs of the VMs

    # Initialize credentials and clients
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    network_client = NetworkManagementClient(credential, subscription_id)
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Create Public IP
    public_ip = create_public_ip(network_client, resource_group_name, location, public_ip_name)
    print(f"Public IP created: {public_ip.id}")

    # Create Load Balancer
    load_balancer = create_load_balancer(network_client, resource_group_name, location, lb_name, public_ip.id)
    print(f"Load Balancer created: {load_balancer.id}")

    # Create Backend Pool
    backend_pool = create_backend_pool(network_client, resource_group_name, lb_name, backend_pool_name)
    print(f"Backend Pool created: {backend_pool.id}")

    # Create Health Probe
    health_probe = create_health_probe(network_client, resource_group_name, lb_name, probe_name)
    print(f"Health Probe created: {health_probe.id}")

    # Create Load Balancing Rule
    frontend_ip_config = load_balancer.frontend_ip_configurations[0].id
    lb_rule = create_lb_rule(network_client, resource_group_name, lb_name, rule_name, frontend_ip_config, backend_pool.id, health_probe.id)
    print(f"Load Balancing Rule created: {lb_rule.id}")

    # Associate NICs with Load Balancer
    for nic_name in vm_nics:
        associate_nic_with_lb(network_client, resource_group_name, nic_name, backend_pool.id)
        print(f"NIC {nic_name} associated with Load Balancer")

if __name__ == "__main__":
    main()