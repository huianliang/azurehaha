from azure.identity import InteractiveBrowserCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryDefinition, QueryTimePeriod, QueryDataset, QueryAggregation, QueryGrouping
from azure.core.exceptions import HttpResponseError
import csv
import datetime
import time
import random

def export_billing_report(subscription_id, tenant_id):
    # Initialize credentials and clients
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    cost_management_client = CostManagementClient(credential)

    # Define the time period for the billing report
    time_period = QueryTimePeriod(
        from_property=(datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
        to=(datetime.datetime.now()).strftime('%Y-%m-%d')
    )

    # Define the base query definition
    query_definition = QueryDefinition(
        type="Usage",
        timeframe="Custom",
        time_period=time_period,
        dataset=QueryDataset(
            granularity="Daily",
            aggregation={
                "totalCost": QueryAggregation(
                    name="PreTaxCost",
                    function="Sum"
                )
            },
            grouping=[
                QueryGrouping(
                    name="ResourceId",
                    type="Dimension"
                ),
                QueryGrouping(
                    name="ResourceType",
                    type="Dimension"
                ),
                QueryGrouping(
                    name="ResourceLocation",
                    type="Dimension"
                ),
                QueryGrouping(
                    name="ResourceGroupName",
                    type="Dimension"
                ),
                QueryGrouping(
                    name="MeterCategory",
                    type="Dimension"
                ),
                QueryGrouping(
                    name="MeterSubCategory",
                    type="Dimension"
                ),
                QueryGrouping(
                    name="ServiceName",
                    type="Dimension"
                )
            ]
        )
    )

    def execute_query_with_retry(scope, parameters, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                return cost_management_client.query.usage(scope=scope, parameters=parameters)
            except HttpResponseError as e:
                if e.status_code == 429:  # Too many requests
                    wait_time = (2 ** retries) + random.uniform(0, 1)
                    print(f"Rate limit hit. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    raise
        raise Exception("Max retries exceeded")

    # Collect cost data for the subscription
    cost_data = []
    result = execute_query_with_retry(scope=f'/subscriptions/{subscription_id}', parameters=query_definition)

    # Debug: Print the result to check if data is returned
    print("Query Result:", result)

    for row in result.rows:
        # Debug: Print each row to check the data
        print("Row:", row)
        cost_data.append(row)

    # Export cost data to CSV
    with open('billing_report_subscription.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ResourceId", "ResourceType", "ResourceLocation", "ResourceGroupName", "MeterCategory", "MeterSubCategory", "ServiceName", "Date", "Cost"])
        writer.writerows(cost_data)

    print("Billing report for the subscription exported to billing_report_subscription.csv")

def main():
    # Replace with your Azure subscription ID and tenant ID
    subscription_id = '16d7b6cf-cfcd-466f-933a-7de50afb11f7'
    tenant_id = '9c33bd1d-9ba6-4240-a5fe-7549c7bbcb17'

    # Export billing report for the subscription
    export_billing_report(subscription_id, tenant_id)

if __name__ == "__main__":
    main()