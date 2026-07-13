from openaq import OpenAQ

client = OpenAQ(api_key='40f7484413a58f2286d1abb283ba6a3ca0771e94f133e37952000b0391c2b324')
result = client.locations.list(coordinates=(5.651221, -0.185531), radius=12000, limit=1000)
client.close()

# Extract location IDs and details
locations = result.results
print(f'Found {len(locations)} locations\n')
for loc in locations:
    print(f'  ID: {loc.id}, Name: {loc.name}')
