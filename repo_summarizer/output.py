from typing import Dict, List


def format_as_tree(file_summaries: Dict) -> str:
    def insert_into_tree(tree: Dict, parts: List[str], summary: str) -> None:
        if len(parts) == 1:
            tree[parts[0]] = summary
        else:
            head, *tail = parts
            if head not in tree:
                tree[head] = {}
            insert_into_tree(tree[head], tail, summary)

    def tree_to_str(tree: Dict, prefix: str = "") -> str:
        lines = []
        items = list(tree.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            current_prefix = prefix + connector
            if isinstance(value, dict):
                lines.append(current_prefix + key)
                child_prefix = prefix + ("    " if is_last else "│   ")
                lines.append(tree_to_str(value, child_prefix))
            else:
                if value == "":
                    lines.append(current_prefix + key)
                else:
                    lines.append(current_prefix + f"{key} - {value}")
        return "\n".join(lines)

    tree = {}
    for path, summary in file_summaries.items():
        parts = path.split("/")
        insert_into_tree(tree, parts, summary)

    return ".\n" + tree_to_str(tree)
