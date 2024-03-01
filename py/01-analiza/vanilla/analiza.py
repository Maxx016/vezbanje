import os
import sys

if not len(sys.argv) < 3:
    if os.path.exists(sys.argv[1]):
        searchString = sys.argv[2]
        if len(sys.argv ) > 3:
            for arg in sys.argv[3:]:
                searchString += " " + arg
        sum = 0.0
        with open(sys.argv[1], "r") as file:
            lines = file.read().splitlines()
            for line in lines[1:]:
                thisLine = line.split(',')
                if thisLine[2].lstrip('"').rstrip('"') == searchString:
                    sum += float(thisLine[1])
        print(f'Sum by name {searchString}: {str(sum)}')
        file.close()
    else:
        print("Path doesn't exist.")
else:
    print("Usage: (file path | string)")