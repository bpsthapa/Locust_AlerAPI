from ID_List import *

print("\n")

# Extract and format IDs
ids = ','.join(f'"{row["id"]}"' for row in data['rows'])


print(ids)

print("\n")



with open("output.txt", "w") as file:
    file.write("\n")

    # Extract and format IDs
    ids = ','.join(f'"{row["id"]}"' for row in data['rows'])

    # Write IDs to the file
    file.write(ids + "\n")