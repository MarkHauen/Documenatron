import hashlib
import os
import sys
from pathlib import Path
from LLMInterface.LLMInterface import send_class_to_llm
from LLMInterface.systemPrompts import FILE_SUMMARY_PROMPT, DIR_SUMMARY_PROMPT, ROOT_SUMMARY_PROMPT

DOCS_DIR_NAME = "_llm_docs"

# Directories to ignore (blacklist)
IGNORED_DIRS = {
    ".git",
    ".svn",
    ".hg",
    ".idea",
    ".vscode",
    ".firebase",
    "bin",
    "obj",
    "lib",
    "docs",
    "assets",
    "node_modules",
    "packages",
    "venv",
    "__pycache__",
    "dist",
    "build",
    DOCS_DIR_NAME
}

# File extensions considered "source code"
SOURCE_EXTENSIONS = {
    ".py", ".cs", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h",
    ".html", ".css", ".scss", ".go", ".rb", ".php", ".swift", ".m", ".mm"
}

def compute_directory_hash(subdir_hashes, file_hashes):
    """Compute a combined hash for a directory from its subdirectory and file hashes."""
    # Sort to ensure consistent order
    all_hashes = sorted(subdir_hashes) + sorted(file_hashes)
    combined = ''.join(all_hashes)
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def read_directory_summary_hash(summary_path: Path) -> str:
    """Read the hash from the first line of a directory summary file, if present."""
    if not summary_path.exists():
        return ""
    try:
        with open(summary_path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline()
            if first_line.startswith("# DIR_HASH: "):
                return first_line.strip().split("# DIR_HASH: ", 1)[1]
    except Exception:
        pass
    return ""

def compute_file_hash(content: str) -> str:
    """Compute SHA256 hash of file content as a hex string."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def read_summary_hash(summary_path: Path) -> str:
    """Read the hash from the first line of a summary file, if present."""
    if not summary_path.exists():
        return ""
    try:
        with open(summary_path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline()
            if first_line.startswith("# HASH: "):
                return first_line.strip().split("# HASH: ", 1)[1]
    except Exception:
        pass
    return ""

def should_ignore_dir(dirname: str) -> bool:
    return dirname in IGNORED_DIRS

def is_source_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in SOURCE_EXTENSIONS

def ensure_docs_dir(path: Path) -> Path:
    # Avoid creating nested _llm_docs directories
    if path.name == DOCS_DIR_NAME:
        return path
    docs_dir = path.joinpath(DOCS_DIR_NAME)
    if not docs_dir.exists():
        os.mkdir(docs_dir)
    return docs_dir

def process_directory(dir_path: Path) -> str:
    """
    Recursively process a directory:
      - Summarize all subdirectories first.
      - Summarize all files.
      - Summarize entire directory based on subdir + file summaries.
    Returns the directory summary text so the parent can include it.
    """
    docs_dir = ensure_docs_dir(dir_path)

    # --- 1. Recurse into subdirectories ---
    subdir_summaries = []
    subdir_hashes = []
    for entry in dir_path.iterdir():
        if entry.is_dir() and not should_ignore_dir(entry.name):
            subdir_summary_text = process_directory(entry)
            # Read the hash from the subdirectory's summary file
            subdir_docs_dir = ensure_docs_dir(entry)
            subdir_summary_file = subdir_docs_dir / "_directory_summary.txt"
            subdir_hash = read_directory_summary_hash(subdir_summary_file)
            if subdir_summary_text.strip():
                subdir_summaries.append(
                    f"### Subdirectory: {entry.name}\n{subdir_summary_text}"
                )
            if subdir_hash:
                subdir_hashes.append(subdir_hash)

    # --- 2. Summarize files in this directory ---
    file_summaries = []
    file_hashes = []
    for entry in dir_path.iterdir():
        if entry.is_file() and is_source_file(entry.name):
            file_summary_path = docs_dir / f"{entry.name}.summary.txt"
            try:
                with open(entry, "r", encoding="utf-8", errors="ignore") as f:
                    code_content = f.read()

                file_hash = compute_file_hash(code_content)
                existing_hash = read_summary_hash(file_summary_path)
                if file_hash == existing_hash:
                    # No change, skip summarizing
                    print(f"Skipping unchanged file: {entry}")
                    # Optionally, read the summary for inclusion in directory summary
                    with open(file_summary_path, "r", encoding="utf-8", errors="ignore") as out:
                        lines = out.readlines()
                        summary_text = ''.join(lines[1:]) if lines and lines[0].startswith('# HASH: ') else ''.join(lines)
                else:
                    print(f"Summarizing file: {entry}")
                    summary_text = send_class_to_llm(code_content, FILE_SUMMARY_PROMPT)
                    with open(file_summary_path, "w", encoding="utf-8") as out:
                        out.write(f"# HASH: {file_hash}\n{summary_text}")

                file_summaries.append(
                    f"### File: {entry.name}\n{summary_text}"
                )
                file_hashes.append(file_hash)
            except Exception as e:
                print(f"Error reading {entry}: {e}")

    # --- 3. Combine subdirectory + file summaries ---
    combined_text_parts = []
    if subdir_summaries:
        combined_text_parts.append("\n\n".join(subdir_summaries))
    if file_summaries:
        combined_text_parts.append("\n\n".join(file_summaries))

    combined_text = "\n\n".join(combined_text_parts).strip()

    # --- 4. Summarize the directory itself if there’s content ---
    dir_summary_text = ""
    dir_summary_file = docs_dir / "_directory_summary.txt"
    dir_hash = compute_directory_hash(subdir_hashes, file_hashes)
    existing_dir_hash = read_directory_summary_hash(dir_summary_file)
    if combined_text:
        if dir_hash == existing_dir_hash:
            print(f"Skipping unchanged directory: {dir_path}")
            # Read the summary for inclusion in parent summary
            try:
                with open(dir_summary_file, "r", encoding="utf-8", errors="ignore") as out:
                    lines = out.readlines()
                    dir_summary_text = ''.join(lines[1:]) if lines and lines[0].startswith('# DIR_HASH: ') else ''.join(lines)
            except Exception:
                dir_summary_text = ''
        else:
            print(f"Summarizing directory: {dir_path}")
            # Check if we are at the root directory
            if dir_path.parent == dir_path:  # This is the root directory
                dir_summary_text = send_class_to_llm(combined_text, ROOT_SUMMARY_PROMPT)
            else:
                dir_summary_text = send_class_to_llm(combined_text, DIR_SUMMARY_PROMPT)

            # Save directory-level summary with hash
            with open(dir_summary_file, "w", encoding="utf-8") as out:
                out.write(f"# DIR_HASH: {dir_hash}\n{dir_summary_text}")

    return dir_summary_text

def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).parent.resolve()
    if not root.exists() or not root.is_dir():
        print(f"Error: The specified root path '{root}' does not exist or is not a directory.")
        sys.exit(1)
    print(f"Starting recursive documentation in: {root}")
    process_directory(root)
    print("Recursive documentation complete!")

if __name__ == "__main__":
    main()