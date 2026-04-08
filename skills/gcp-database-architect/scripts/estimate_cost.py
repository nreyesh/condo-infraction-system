import argparse
import sys

def calculate_gcp_cost(instance_type, storage_gb, region="southamerica-west1"):
    """
    Calculates estimated monthly cost for Cloud SQL.
    Formula: (Instance_rate * 730) + (Storage_gb * Rate)
    Values are approximations for southamerica-west1 (Santiago).
    """
    
    # Approx rates for Cloud SQL (PostgreSQL/MySQL) in southamerica-west1
    RATES = {
        "db-f1-micro": 0.015, # $10.95/mo
        "db-g1-small": 0.035, # $25.55/mo
        "db-custom-1-3840": 0.075, # 1 vCPU, 3.75GB RAM ~ $54.75/mo
        "db-custom-2-7680": 0.150, # 2 vCPU, 7.5GB RAM ~ $109.50/mo
    }
    
    STORAGE_RATE = 0.230 # $0.23 per GB per month (SSD)
    
    instance_rate = RATES.get(instance_type, 0.075)
    
    monthly_instance = instance_rate * 730
    monthly_storage = storage_gb * STORAGE_RATE
    total = monthly_instance + monthly_storage
    
    return {
        "instance_monthly": round(monthly_instance, 2),
        "storage_monthly": round(monthly_storage, 2),
        "total_monthly": round(total, 2),
        "region": region,
        "instance_type": instance_type,
        "storage_gb": storage_gb
    }

def main():
    parser = argparse.ArgumentParser(description="Estimate monthly cost for GCP Cloud SQL (Santiago region)")
    parser.add_argument("--instance", default="db-f1-micro", help="Instance type (db-f1-micro, db-g1-small, db-custom-1-3840)")
    parser.add_argument("--storage", type=int, default=10, help="Storage in GB (e.g. 10, 100)")
    
    args = parser.parse_args()
    
    cost = calculate_gcp_cost(args.instance, args.storage)
    
    print("\n" + "="*40)
    print(" GCP CLOUD SQL COST ESTIMATE (SANTIAGO)")
    print("="*40)
    print(f" Instance: {cost['instance_type']:<20} | ${cost['instance_monthly']:>7}/mo")
    print(f" Storage:  {cost['storage_gb']:>3} GB SSD        | ${cost['storage_monthly']:>7}/mo")
    print("-" * 40)
    print(f" TOTAL ESTIMATED MONTHLY:        | ${cost['total_monthly']:>7}/mo")
    print("="*40)
    print(" Note: Prices are approximate and exclude networking (egress) or backups.")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
