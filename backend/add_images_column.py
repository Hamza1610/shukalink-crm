import os
import sys
from sqlalchemy import create_engine, text

# Add backend directory to path to allow imports of 'app'
# This assumes the script is located in /backend/
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

print(f"Backend directory added to path: {backend_dir}")

try:
    from app.core.config import settings
    print("Successfully imported settings.")
except ImportError as e:
    print(f"Failed to import settings: {e}")
    sys.exit(1)

def migrate():
    print("Running migration to add images column to produce_listings...")
    
    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        
        with engine.connect() as connection:
            # Check if column exists
            print("Checking if column 'images' exists...")
            result = connection.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='produce_listings' AND column_name='images'"
            ))
            
            if result.fetchone():
                print("Column 'images' already exists.")
            else:
                # Add column
                print("Column 'images' not found. Adding it...")
                connection.execute(text("ALTER TABLE produce_listings ADD COLUMN images JSONB"))
                connection.commit()
                print("Successfully added 'images' column.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        # Print full traceback
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()
