from jmx_builder.models.tree import TreeElement


def print_tree(root: TreeElement, indent: str = "", is_last: bool = True) -> str:
    connector = "└── " if is_last else "├── "
    result = indent + connector + root.testname + "\n"
    
    indent += "    " if is_last else "│   "
    
    for i, child in enumerate(root.children):
        is_last_child = (i == len(root.children) - 1)
        result += print_tree(child, indent, is_last_child)
    
    return result

