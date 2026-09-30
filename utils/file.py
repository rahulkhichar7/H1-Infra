import os


def folder_traversal(
    root_dir,
    exclude_folders={".git", "__pycache__", "venv"},
    exclude_files={".gitignore"},
    exclude_formats={".pth", ".png", ".jpg"}
):
    exclude_folders = set(exclude_folders)
    exclude_files = set(exclude_files)
    exclude_formats = {ext.lower() for ext in exclude_formats}

    tree = []

    def dfs(current_dir, depth=0):
        try:
            entries = sorted(os.scandir(current_dir), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return

        for entry in entries:

            if entry.is_dir():
                if entry.name in exclude_folders:
                    continue

                tree.append(
                    f"{'    ' * depth}📁 {entry.name}"
                )

                dfs(entry.path, depth + 1)

            elif entry.is_file():
                if entry.name in exclude_files:
                    continue

                extension = os.path.splitext(entry.name)[1].lower()

                if extension in exclude_formats:
                    continue

                tree.append(
                    f"{'    ' * depth}📄 {entry.name}"
                )

                try:
                    with open(entry.path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for line in content.splitlines():
                        tree.append(f"{'    ' * (depth + 1)}{line}")

                except (UnicodeDecodeError, PermissionError):
                    tree.append(f"{'    ' * (depth + 1)}[Cannot read file]")

    root_dir = os.path.abspath(root_dir)

    tree.append(f"📁 {os.path.basename(root_dir)}")

    dfs(root_dir, 1)

    return "\n".join(tree)