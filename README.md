# Documenatron

Documenatron is a Python tool for recursively generating documentation summaries for source code projects using an LLM (Large Language Model). It traverses your project directory, summarizes each source file, and creates directory-level and project-level summaries. The tool is efficient for continuous development, only re-summarizing files that have changed.

## Features
- Recursively traverses project directories
- Summarizes source files using an LLM
- Creates directory and project-level summaries
- Skips unchanged files using content hashes for efficiency
- Ignores common build, virtual environment, and documentation directories

## How It Works
1. For each source file, computes a SHA256 hash of its contents.
2. Stores the hash at the top of the corresponding summary file.
3. On subsequent runs, only re-summarizes files whose content has changed.
4. Summaries are stored in a `_llm_docs` directory within each processed directory.

## Supported Source File Types
- Python, C#, JavaScript, TypeScript, Java, C/C++, HTML, CSS, Go, Ruby, PHP, Swift, Objective-C, and more.

## Usage

### Prerequisites
- Python 3.7+
- An implementation of `send_class_to_llm` in `LLMInterface/LLMInterface.py` that connects to your LLM provider - Currently configured for running Mistal on a local Ollama instance. 

### Running the Script

```sh
python generate_docs.py [project_root]
```
- If `project_root` is omitted, the script uses its own directory as the root.

### Output
- Documentation summaries are written to `_llm_docs` directories throughout your project.
- Each summary file includes a hash for change tracking.
- Directory and project summaries are also generated.

## Customization
- Update `IGNORED_DIRS` and `SOURCE_EXTENSIONS` in `generate_docs.py` to fit your project.
- Modify prompt templates in `LLMInterface/systemPrompts.py` for different summary styles.

## Example Directory Structure
```
project_root/
├── generate_docs.py
├── LLMInterface/
│   ├── LLMInterface.py
│   └── systemPrompts.py
├── my_code.py
├── _llm_docs/
│   ├── my_code.py.summary.txt
│   └── _directory_summary.txt
└── ...
```

## License
MIT License
