# alias2symlink

## Introduction

`alias2symlink` is a tool designed to convert macOS alias files to symbolic links. This can be particularly useful for users who want to manage their file system more efficiently and ensure compatibility with various applications that may not recognize macOS alias files.

## Features

- Convert macOS alias files to symbolic links.
- Handle nested directories and files.
- Prevent infinite recursion by detecting self-references and parent directory references.

## Installation

To install `alias2symlink`, clone the repository and run the setup script:

```sh
git clone https://github.com/guido233/alias2symlink.git
cd alias2symlink
```

## Usage

To use `alias2symlink`, run the following command:

```sh
python main.py test_folder
```

This will convert all alias files within the specified directory to symbolic links.

## Recursion Handling

There is an issue in the current code regarding recursion. For example, if there is an alias of the folder within the folder to be processed, it will cause infinite recursion.

This issue does not exist if the folder structure is standardized. For instance, if a folder is named "Sports", its subfolders should not be named "Sports" as well, as this would lead to infinite recursion. Categories should become more specific and should not reference themselves.

However, users might encounter this situation. To handle this, if there is a self-reference or a reference to a parent directory, the recursion should stop and return immediately.

## To Do

- Implement functionality to convert symbolic links back to macOS alias files.
- Use different methods based on the operating system to ensure compatibility and improve the utility of links across different systems.

## License

This project is licensed under the MIT License.
