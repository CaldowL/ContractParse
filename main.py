import os
import json

from ContractParser import ContractParser

if __name__ == "__main__":
    parser = ContractParser()
    query = [os.path.abspath(os.path.join("files", i)) for i in os.listdir("files")]
    results = parser.parse_contract(query)
    print(json.dumps(results, ensure_ascii=False))
