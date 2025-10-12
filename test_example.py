#!/usr/bin/env python3
"""
Example Python file for testing the offline coding agent
"""

import os
import sys
from pathlib import Path


def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)


def find_files_by_extension(directory, extension):
    """Find all files with a specific extension in a directory."""
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(extension):
                files.append(os.path.join(root, filename))
    return files


class FileProcessor:
    """A class to process files in various ways."""

    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.processed_files = []

    def process_file(self, file_path):
        """Process a single file."""
        full_path = self.base_path / file_path
        if full_path.exists():
            # Placeholder for file processing logic
            self.processed_files.append(str(full_path))
            return True
        return False

    def get_statistics(self):
        """Get processing statistics."""
        return {
            'total_processed': len(self.processed_files),
            'files': self.processed_files
        }


def main():
    """Main function to demonstrate the file processor."""
    processor = FileProcessor('.')

    # Example usage
    test_files = ['README.md', 'requirements.txt']

    for file_name in test_files:
        success = processor.process_file(file_name)
        print(f"Processed {file_name}: {'Success' if success else 'Failed'}")

    stats = processor.get_statistics()
    print(f"Statistics: {stats}")


if __name__ == '__main__':
    main()