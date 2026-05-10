from database import MindMapDB

def run_test():
    db = MindMapDB()

    # 1. Add Hebrew concepts
    print("Saving data to DB...")
    c1 = db.add_concept("Artificial Intelligence", "Technology")
    c2 = db.add_concept("Machine learning", "algorithms")
    
    if c1 and c2:
        print(f"Successfully saved concepts with IDs: {c1}, {c2}")

    # 2. Retrieve and display data
    print("\nRetrieving data from DB:")
    results = db.get_all_concepts()
    
    for row in results:
        print(f"ID: {row['id']} | Label: {row['label']} | Category: {row['category']}")

if __name__ == "__main__":
    run_test()