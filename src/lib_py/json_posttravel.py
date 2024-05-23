import json

def postorder_traversal(node):
    if node is None:
        return []
    
    left_result = postorder_traversal(node.get("left"))
    right_result = postorder_traversal(node.get("right"))
    
    return left_result + right_result + [node["value"]]

# 從檔案中讀取 JSON 數據
with open('binary_tree.json', 'r') as file:
    tree_json = json.load(file)

# 輸出結果
print(postorder_traversal(tree_json))
