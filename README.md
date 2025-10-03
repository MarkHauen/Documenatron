# Documenatron

Documenatron is a Python tool for recursively generating documentation summaries for source code projects using an LLM (Large Language Model). It traverses your project directory, summarizes each source file, and creates directory-level and project-level summaries. The tool is efficient for continuous development, only re-summarizing files that have changed.

## Features
- Recursively traverses project directories
- Summarizes source files using an LLM
- Creates directory and project-level summaries
- Skips unchanged files using content hashes for efficiency
- Force regeneration mode to update all documentation
- Project context support via README to provide better contextual documentation
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

**Basic usage:**
```sh
python generate_docs.py [project_root]
```
- If `project_root` is omitted, the script uses its own directory as the root.

**Force regeneration (update all documentation):**
```sh
python generate_docs.py [project_root] -f
```
- Use the `-f` or `--force` flag to regenerate all documentation, even for unchanged files.
- Useful when switching LLM models or updating documentation style.

**With project context:**
```sh
python generate_docs.py [project_root] --readme path/to/README.md
```
- The `--readme` option provides project context to the LLM for more contextual documentation.
- The LLM will understand how each component fits into the overall project architecture.

**Combined example:**
```sh
python generate_docs.py C:\MyProject --readme C:\MyProject\README.md -f
```

### Output
- Documentation summaries are written to `_llm_docs` directories throughout your project.
- Each summary file includes a hash for change tracking.
- Directory and project summaries are also generated.

### Post-Processing Documentation

**Cleaning DeepSeek `<think>` tags:**

If you're using DeepSeek models (which output reasoning in `<think>` tags), you can clean up the documentation files:

```sh
python clean_documentation.py [project_root]
```
- Recursively removes all `<think>...</think>` blocks from documentation files
- Reduces token count and removes reasoning artifacts
- Safe to run multiple times (only processes files with `<think>` tags)

**Dry-run mode (preview changes):**
```sh
python clean_documentation.py [project_root] --dry-run
```
- Shows what would be cleaned without making changes

**Example:**
```sh
# Generate documentation with DeepSeek model
python generate_docs.py C:\MyProject --readme C:\MyProject\README.md

# Clean up the <think> tags
python clean_documentation.py C:\MyProject
```

## Customization
- Update `IGNORED_DIRS` and `SOURCE_EXTENSIONS` in `generate_docs.py` to fit your project.
- Modify prompt templates in `LLMInterface/systemPrompts.py` for different summary styles.



## License
MIT License
