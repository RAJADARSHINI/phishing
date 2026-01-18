"""
Helper script to set up data directory and check CSV files

This script helps organize CSV files for training.
"""

import os
import shutil
import sys

def setup_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
    else:
        print(f"Directory already exists: {data_dir}")
    return data_dir


def find_csv_files():
    """Find CSV files in common locations"""
    csv_files = {
        'enron_spam.csv': None,
        'phishing_sites.csv': None
    }
    
    # Search in current directory and parent directories
    search_paths = [
        '.',
        '..',
        '../..',
        os.path.join(os.path.dirname(__file__), '..'),
    ]
    
    # Also check common download locations
    home_dir = os.path.expanduser('~')
    if home_dir:
        search_paths.extend([
            os.path.join(home_dir, 'Downloads'),
            os.path.join(home_dir, 'Desktop'),
        ])
    
    for path in search_paths:
        for filename in csv_files.keys():
            filepath = os.path.join(path, filename)
            if os.path.exists(filepath):
                csv_files[filename] = filepath
                print(f"Found {filename} at: {filepath}")
    
    return csv_files


def copy_csv_files(csv_files, data_dir):
    """Copy CSV files to data directory"""
    for filename, source_path in csv_files.items():
        if source_path:
            dest_path = os.path.join(data_dir, filename)
            if not os.path.exists(dest_path):
                shutil.copy2(source_path, dest_path)
                print(f"Copied {filename} to {dest_path}")
            else:
                print(f"{filename} already exists in data directory")
        else:
            print(f"Warning: {filename} not found")


def check_csv_structure(filepath):
    """Check if CSV file has the expected structure"""
    import pandas as pd
    try:
        df = pd.read_csv(filepath, nrows=5)
        print(f"\nChecking {os.path.basename(filepath)}:")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Rows (sample): {len(df)}")
        
        # Check for required columns
        has_text = 'text' in df.columns
        has_label = any(col in df.columns for col in ['labels', 'label', 'spam', 'phishing'])
        
        if has_text and has_label:
            print(f"  ✓ Structure looks good")
        else:
            print(f"  ⚠ Missing required columns. Expected 'text' and one of: 'labels', 'label', 'spam', 'phishing'")
        
        return has_text and has_label
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return False


def main():
    """Main setup function"""
    print("="*50)
    print("Data Setup Helper")
    print("="*50)
    
    # Create data directory
    data_dir = setup_data_directory()
    
    # Find CSV files
    print("\nSearching for CSV files...")
    csv_files = find_csv_files()
    
    # Copy files to data directory
    print("\nCopying files to data directory...")
    copy_csv_files(csv_files, data_dir)
    
    # Check file structure
    print("\nChecking file structure...")
    for filename in ['enron_spam.csv', 'phishing_sites.csv']:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            check_csv_structure(filepath)
        else:
            print(f"\n{filename} not found in data directory")
            print(f"  Please place {filename} in the data/ directory")
    
    print("\n" + "="*50)
    print("Setup complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Ensure both CSV files are in the data/ directory")
    print("2. Run: python train_models.py")
    print("3. Start the API: python app.py")


if __name__ == '__main__':
    main()
