from scraper.sites import get_site_resources
from scraper.medium import get_medium_resources

print("Testing Sites...")
sites_result = get_site_resources("python")
print(f"Sites found: {len(sites_result)}")
if sites_result:
    print(sites_result[0])

print("\nTesting Medium...")
medium_result = get_medium_resources("python")
print(f"Medium found: {len(medium_result)}")
if medium_result:
    print(medium_result[0])
