import sys
import os
import pandas as pd
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.processor import ReviewProcessor

def test_pii_stripping():
    processor = ReviewProcessor()
    test_cases = [
        ("Contact me at shraddha@example.com", "Contact me at [EMAIL]"),
        ("Hey @shraddha check this", "Hey [USER] check this"),
        ("My order ID is 123456789", "My order ID is [ID]"),
        ("Check out https://google.com", "Check out https://google.com"), # URL should stay
    ]
    
    print("Running PII Stripping Tests...")
    for input_text, expected in test_cases:
        result = processor.strip_pii(input_text)
        assert result == expected, f"Failed: Expected '{expected}', got '{result}'"
    print("✅ PII Stripping Tests Passed!")

def test_large_batch_processing():
    print("\nSimulating 1000 Reviews Batch...")
    # Create a dummy CSV with 1000 rows
    data = {
        'rating': [5] * 1000,
        'text': [f"This is review number {i} with fake@email.com and @user{i}" for i in range(1000)]
    }
    df = pd.DataFrame(data)
    temp_csv = "tests/phase1/temp_test_1000.csv"
    df.to_csv(temp_csv, index=False)
    
    processor = ReviewProcessor()
    reviews = processor.process_csv(temp_csv)
    
    assert len(reviews) == 1000, f"Failed: Expected 1000 reviews, got {len(reviews)}"
    assert "[EMAIL]" in reviews[0]['text'], "Failed: Email not stripped in batch"
    assert "[USER]" in reviews[0]['text'], "Failed: User mention not stripped in batch"
    
    os.remove(temp_csv)
    print("✅ 1000 Reviews Batch Processing Passed!")

def test_actual_sample_data():
    print("\nValidating actual data/sample_reviews.csv...")
    file_path = "/Users/khageshbhadane/Shraddha Jagtap/First-Gen-AI-App-Review-Insights-Analyse/data/sample_reviews.csv"
    
    if not os.path.exists(file_path):
        print("❌ sample_reviews.csv not found!")
        return

    processor = ReviewProcessor()
    reviews = processor.process_csv(file_path)
    
    print(f"Loaded {len(reviews)} reviews from CSV.")
    assert len(reviews) >= 200, f"Failed: Expected at least 200 reviews, got {len(reviews)}"
    
    # Check for any remaining 'title' key which should have been removed
    if reviews and 'title' in reviews[0]:
         assert False, "Failed: 'title' column still present in processed output"
    
    print("✅ actual data/sample_reviews.csv Validation Passed!")

if __name__ == "__main__":
    try:
        test_pii_stripping()
        test_large_batch_processing()
        test_actual_sample_data()
        print("\n🎉 All Phase 1 Tests Passed for the Updated Dataset!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)
