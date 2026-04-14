import json
import random

# Entity Data
names = ["John Doe", "Jane Smith", "Alice Johnson", "Bob Brown", "Charlie Davis", "Emily Wilson", "Michael Clark", "Sarah Lewis", "David Hall", "Emma White"]
phones = ["555-0123", "555-0199", "+1-555-0100", "(555) 012-3456", "555-1234", "+44 7700 900077", "123-456-7890", "987-654-3210"]
emails = ["john@email.com", "jane.smith@test.org", "contact@company.net", "support@helpdesk.io", "alice.j@domain.co", "bob123@web.com"]
addresses = ["123 Main St, New York, NY", "456 Elm Ave, Los Angeles, CA", "789 Oak Ln, Chicago, IL", "101 Pine Rd, Seattle, WA", "202 Maple Dr, Austin, TX"]
order_ids = ["OD12345", "OD67890", "ORD-4567", "#998877", "TRX-112233", "OD-554433", "ORDER#123", "Purchase-789"]
dates = ["2023-10-25", "15th November 2023", "tomorrow", "next Monday", "2024-01-01", "last Friday", "05/12/2023"]
products = ["Wireless Headphones", "Smart Watch", "Gaming Laptop", "Coffee Maker", "Running Shoes", "Smartphone Case", "Bluetooth Speaker", "4K Monitor"]

# Templates
templates = [
    "Hi, this is {CUSTOMER_NAME}. My order {ORDER_ID} hasn't arrived.",
    "Please contact me at {EMAIL} regarding my purchase of {PRODUCT}.",
    "My phone number is {PHONE_NUMBER}. I ordered {PRODUCT} on {DATE}.",
    "Ship to {ADDRESS}. Order ID: {ORDER_ID}.",
    "{CUSTOMER_NAME} here. I have an issue with order {ORDER_ID}.",
    "Can you check the status of {PRODUCT} ordered on {DATE}?",
    "My email is {EMAIL} and phone is {PHONE_NUMBER}.",
    "I moved to {ADDRESS}. Please update my profile.",
    "Refund request for {ORDER_ID} ({PRODUCT}).",
    "Call me at {PHONE_NUMBER} or email {EMAIL}.",
    "Order {ORDER_ID} for {CUSTOMER_NAME} at {ADDRESS}.",
    "I bought {PRODUCT} on {DATE} but it's defective.",
    "Is {PRODUCT} available? Contact {EMAIL}.",
    "Delivery for {CUSTOMER_NAME}, {ADDRESS}, Phone: {PHONE_NUMBER}.",
    "Update: {DATE} is the new delivery date for {ORDER_ID}."
]

def generate_data(num_samples=500):
    training_data = []
    
    for _ in range(num_samples):
        template = random.choice(templates)
        entities = {}
        
        # Select random entities
        entities["CUSTOMER_NAME"] = random.choice(names)
        entities["PHONE_NUMBER"] = random.choice(phones)
        entities["EMAIL"] = random.choice(emails)
        entities["ADDRESS"] = random.choice(addresses)
        entities["ORDER_ID"] = random.choice(order_ids)
        entities["DATE"] = random.choice(dates)
        entities["PRODUCT"] = random.choice(products)
        
        # Correct greedy approach for multi-replace overlap issues:
        # Adjust entity positions? 
        # Wait, if I replace {A} with 'ValA', then {B} position shifts? Yes.
        # So I must not find valid indices AFTER replacing previous ones unless I re-calculate.
        # But `replace` changes the string.
        # 
        # Correct greedy approach:
        # 1. Identify all placeholders in the template.
        # 2. Sort them by position (though template logic usually is linear).
        # 3. Build the new string and record segments.
        
        # Re-doing the loop for correctness:
        parts = []
        last_pos = 0
        current_text_len = 0
        current_annotations = []
        
        # Find all placeholders and their positions in the *original* template
        import re
        # Find all {KEY} patterns
        matches = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r"\{([A-Z_]+)\}", template)]
        # Sort by start position
        matches.sort()
        
        new_text = ""
        last_idx = 0
        
        for start, end, label in matches:
            # Add text before the placeholder
            prefix = template[last_idx:start]
            new_text += prefix
            
            # Add the entity value
            val = entities[label]
            entity_start = len(new_text)
            new_text += val
            entity_end = len(new_text)
            
            current_annotations.append((entity_start, entity_end, label))
            
            last_idx = end
            
        # Add remaining text
        new_text += template[last_idx:]
        
        training_data.append((new_text, {"entities": current_annotations}))

    return training_data

if __name__ == "__main__":
    data = generate_data(500)
    
    # Add the specific example from the prompt to ensure it works perfect
    prompt_example = (
        "Hi, this is John Doe. My order OD12345 hasn’t arrived. Please contact me at john@email.com",
        {"entities": [
            (12, 20, "CUSTOMER_NAME"),
            (30, 37, "ORDER_ID"),
            (76, 90, "EMAIL")
        ]}
    )
    data.append(prompt_example)
    
    with open("data/training_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Generated {len(data)} annotated training samples.")
