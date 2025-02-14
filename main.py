import os
import subprocess
from pathlib import Path
import platform
import shutil
import argparse  # Add argparse for command-line arguments

def is_alias_file(file_path):
    """
    Check if the file is a Mac OS alias file
    
    Args:
        file_path: File path
        
    Returns:
        Boolean indicating whether it is an alias file
    """
    try:
        # Use the mdls command to get the file type
        cmd = ['mdls', '-name', 'kMDItemKind', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            # Check if the output contains the keyword "alias"
            return 'alias' in output.lower()
        return False
    except Exception:
        return False

def resolve_alias(alias_path):
    """
    Resolve Mac OS alias file and return the original file path
    
    Args:
        alias_path: Path to the alias file
        
    Returns:
        String of the original file path if successful
        Empty string if failed
    """
    try:
        # Ensure we are running on MacOS
        if platform.system() != 'Darwin':
            raise RuntimeError("This script can only run on MacOS")
            
        # Normalize the path
        alias_path = os.path.expanduser(alias_path)
        alias_path = os.path.abspath(alias_path)
        
        # Check if the file exists
        if not os.path.exists(alias_path):
            raise FileNotFoundError(f"File not found: {alias_path}")
            
        # Use osascript command to resolve the alias
        cmd = f'''osascript -e 'tell application "Finder"
            set aliasFile to POSIX file "{alias_path}" as alias
            set originalItem to original item of aliasFile
            POSIX path of (originalItem as text)
        end tell' '''
        
        # Execute the command and get the output
        result = os.popen(cmd).read().strip()
        
        if result:
            # Check if it references itself or the parent directory
            if result == alias_path or result.startswith(os.path.dirname(alias_path)):
                raise RuntimeError("Alias file references itself or the parent directory, avoiding infinite recursion")
            return result
        else:
            raise RuntimeError("Unable to resolve alias file")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return ""

def convert_aliases_to_symlinks(folder_path, recursive=True):
    """
    Convert all alias files in the specified folder to symlinks
    
    Args:
        folder_path: Path to the folder to process
        recursive: Whether to recursively process subfolders, default is True
    
    Returns:
        Number of successful conversions, number of failures
    """
    success_count = 0
    failure_count = 0
    
    try:
        # Ensure the folder path is an absolute path
        folder_path = os.path.abspath(os.path.expanduser(folder_path))
        
        # Check if the folder exists
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"Path is not a valid folder: {folder_path}")
        
        # Define the traversal function
        def process_folder(current_folder):
            nonlocal success_count, failure_count
            
            # Get all items in the folder
            items = os.listdir(current_folder)
            
            for item in items:
                item_path = os.path.join(current_folder, item)
                
                # Skip files starting with .
                if item.startswith('.'):
                    continue
                
                # If it is a folder and needs to be processed recursively
                if os.path.isdir(item_path) and recursive:
                    try:
                        # Check if it is an alias file and resolve it
                        if is_alias_file(item_path):
                            original_path = resolve_alias(item_path)
                            # Check if it references itself or the parent directory
                            if original_path == current_folder or original_path.startswith(os.path.dirname(current_folder)):
                                print(f"Skipping recursive reference: {item_path}")
                                continue
                    except RuntimeError as e:
                        print(f"Skipping recursive reference: {item_path}")
                        continue
                    process_folder(item_path)
                    continue
                
                try:
                    # First check if it is an alias file
                    if not is_alias_file(item_path):
                        continue
                    
                    # Try to resolve the alias file
                    original_path = resolve_alias(item_path)
                    
                    if original_path:
                        # Backup the original alias file, use . to hide it
                        backup_path = os.path.join(current_folder, f".{item}.backup")
                        shutil.move(item_path, backup_path)
                        
                        # Create a symlink
                        os.symlink(original_path, item_path)
                        
                        print(f"Success: {item_path} -> {original_path}")
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception as e:
                    print(f"Failed to process file {item_path}: {str(e)}")
                    failure_count += 1
                    continue
        
        # Start processing the folder
        process_folder(folder_path)
        
        return success_count, failure_count
        
    except Exception as e:
        print(f"Error processing folder: {str(e)}")
        return success_count, failure_count

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert macOS alias files to symbolic links.")
    parser.add_argument("folder_path", help="Path to the folder to process")
    args = parser.parse_args()

    # Use the provided folder_path
    folder_path = args.folder_path
    success, failure = convert_aliases_to_symlinks(folder_path)
    print(f"\nConversion complete:")
    print(f"Success: {success} files")
    print(f"Failure: {failure} files")