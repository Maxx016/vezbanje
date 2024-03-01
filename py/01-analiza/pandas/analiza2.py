import pandas as pd
import os
import sys

if not len(sys.argv) < 3:
    if os.path.exists(sys.argv[1]):
        searchString = sys.argv[2]
        if len(sys.argv) > 3:
            for arg in sys.argv[3:]:
                searchString += " " + arg
        sum = 0.0
        table = pd.read_csv(sys.argv[1])
        table2 = table[table.iloc[:, 2].str.lstrip('"').str.rstrip('"') == searchString]
        print(table2)
        sum = table2.iloc[:, 1].astype(float).sum()
        print(f'Sum by name {searchString}: {sum}')
    else:
        print("Path doesn't exist.")
else:
    print("Usage: (file path | string)")