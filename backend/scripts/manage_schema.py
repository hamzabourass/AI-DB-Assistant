"""Script to manage database schema knowledge."""
import os
import sys
import argparse

# Add the parent directory to the path so we can import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vector_db import VectorDBService

def initialize_schema(schema_file="db_schema.txt"):
    """Initialize or update the db_schema.txt file."""
    # Create knowledge directory if it doesn't exist
    knowledge_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge")
    os.makedirs(knowledge_dir, exist_ok=True)
    
    schema_path = os.path.join(knowledge_dir, schema_file)
    
    # Check if schema file exists
    if os.path.exists(schema_path):
        print(f"Schema file '{schema_file}' already exists at {schema_path}")
        
        # Ask for confirmation to reindex
        response = input("Do you want to reindex the vector database? (y/n): ")
        
        if response.lower() == 'y':
            # Reindex the vector database
            vector_db = VectorDBService()
            success = vector_db.index_documents()
            
            if success:
                print("Vector database reindexed successfully!")
            else:
                print("Failed to reindex vector database.")
        else:
            print("Reindexing cancelled.")
    else:
        print(f"Schema file '{schema_file}' not found at {schema_path}")
        print(f"You need to create this file with your database schema information.")
        print(f"After creating the file, run this script again to index it.")

def update_schema_from_file(input_file, schema_file="db_schema.txt"):
    """Update the db_schema.txt file from an input file."""
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' not found.")
        return False
    
    # Create knowledge directory if it doesn't exist
    knowledge_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge")
    os.makedirs(knowledge_dir, exist_ok=True)
    
    schema_path = os.path.join(knowledge_dir, schema_file)
    
    try:
        # Copy content from input file to schema file
        with open(input_file, 'r') as source, open(schema_path, 'w') as target:
            target.write(source.read())
        
        print(f"Schema file '{schema_file}' updated successfully!")
        
        # Reindex the vector database
        vector_db = VectorDBService()
        success = vector_db.clear_and_reindex()
        
        if success:
            print("Vector database reindexed successfully!")
        else:
            print("Failed to reindex vector database.")
        
        return True
    except Exception as e:
        print(f"Error updating schema file: {e}")
        return False

def main():
    """Main function to parse arguments and execute commands."""
    parser = argparse.ArgumentParser(description='Manage database schema knowledge.')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize or check schema file')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update schema from input file')
    update_parser.add_argument('input_file', help='Path to input file')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        initialize_schema()
    elif args.command == 'update':
        update_schema_from_file(args.input_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()