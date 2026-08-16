"""Script to rename documentation files and directories to kebab-case and update internal markdown links."""

from pathlib import Path


def to_kebab_case(name: str) -> str:
    """Convert string with underscores to kebab-case (hyphens)."""
    return name.replace("_", "-")


def rename_files_and_dirs(root_dir: Path) -> dict[Path, Path]:
    """Rename all files and directories under root_dir to kebab-case.

    Returns a mapping of old Path -> new Path.
    """
    renamed_map: dict[Path, Path] = {}

    if not root_dir.exists():
        return renamed_map

    # Process bottom-up to avoid invalidating paths during parent directory renames
    all_paths = sorted(root_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True)

    for path in all_paths:
        if not path.exists():
            continue

        name = path.name
        new_name = to_kebab_case(name)

        if name != new_name:
            target_path = path.parent / new_name

            if path.is_dir():
                if target_path.exists():
                    # Move all items inside path into target_path
                    for child in path.iterdir():
                        destination = target_path / child.name
                        if destination.exists() and destination.is_dir():
                            for subchild in child.iterdir():
                                subchild.rename(destination / subchild.name)
                            child.rmdir()
                        else:
                            child.rename(destination)
                    path.rmdir()
                    renamed_map[path] = target_path
                    print(f"Merged directory {path} -> {target_path}")
                else:
                    path.rename(target_path)
                    renamed_map[path] = target_path
                    print(f"Renamed directory {path} -> {target_path}")
            elif path.is_file():
                if target_path.exists() and target_path != path:
                    print(
                        f"Warning: target file {target_path} already exists."
                        f" Overwriting with {path}"
                    )
                    target_path.unlink()
                path.rename(target_path)
                renamed_map[path] = target_path
                print(f"Renamed file {path} -> {target_path}")

    return renamed_map


def update_markdown_links(search_dirs: list[Path]) -> None:
    """Update internal markdown links across all .md files in search_dirs."""
    for s_dir in search_dirs:
        if not s_dir.exists():
            continue

        for md_file in s_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            original_content = content

            # Fix underscore links in markdown hrefs and inline texts
            # e.g., 01_introduction_and_goals.md -> 01-introduction-and-goals.md
            # 09_architecture_decisions -> 09-architecture-decisions
            lines = content.splitlines(keepends=True)
            updated_lines = []

            for line in lines:
                # We target words with underscores inside links or filenames
                new_line = line
                # Replace specific known underscores in arc42 filenames
                replacements = [
                    ("01_introduction_and_goals", "01-introduction-and-goals"),
                    (
                        "02_architecture_constraints",
                        "02-architecture-constraints",
                    ),
                    ("03_context_and_scope", "03-context-and-scope"),
                    ("04_solution_strategy", "04-solution-strategy"),
                    ("05_building_block_view", "05-building-block-view"),
                    ("06_runtime_view", "06-runtime-view"),
                    ("07_deployment_view", "07-deployment-view"),
                    ("08_cross_cutting_concepts", "08-cross-cutting-concepts"),
                    (
                        "09_architecture_decisions",
                        "09-architecture-decisions",
                    ),
                    ("10_quality_requirements", "10-quality-requirements"),
                    (
                        "11_risks_and_technical_debt",
                        "11-risks-and-technical-debt",
                    ),
                    ("12_glossary", "12-glossary"),
                ]
                for old_sub, new_sub in replacements:
                    new_line = new_line.replace(old_sub, new_sub)

                updated_lines.append(new_line)

            new_content = "".join(updated_lines)
            if new_content != original_content:
                md_file.write_text(new_content, encoding="utf-8")
                print(f"Updated links in {md_file}")


def main() -> None:
    root = Path(".")
    docs_dirs = [root / "docs", root / "docs-2"]

    for d in docs_dirs:
        if d.exists():
            print(f"--- Renaming files/dirs in {d} ---")
            rename_files_and_dirs(d)

    print("--- Updating markdown links ---")
    update_markdown_links(docs_dirs)


if __name__ == "__main__":
    main()
