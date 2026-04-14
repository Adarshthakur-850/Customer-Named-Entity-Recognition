
import spacy
import sys
import os
import re
import json

def load_model(model_dir="model"):
    if not os.path.exists(model_dir):
        print(f"Model directory not found at {model_dir}. Please train the model first.")
        return None
    nlp = spacy.load(model_dir)
    return nlp

def extract_entities(text, nlp):
    entities = {}
    
    # 1. Regex Extraction (High Precision for specific formats)
    
    # Email Regex
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    if emails:
        entities["EMAIL"] = emails[0] # Taking the first one for simplicity, or list them
    
    # Phone Regex (Simple pattern to match generated data)
    # Matches: 555-0123, +1-555..., (555) ...
    phone_pattern = r"(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}"
    phones = re.findall(phone_pattern, text)
    if phones:
        # re.findall with groups returns tuples, we need full match.
        # Let's use finditer for full match
        phone_matches = [m.group(0) for m in re.finditer(phone_pattern, text)]
        if phone_matches:
             entities["PHONE_NUMBER"] = phone_matches[0]

    # Order ID Regex
    # Matches: OD12345, ORD-4567, #998877, etc. based on generation logic
    # Heuristic: OD followed by digits, or ORD-, or # followed by digits
    order_pattern = r"(OD\d+|ORD-\d+|#\d+|TRX-\d+|ORDER#\d+|Purchase-\d+|OD-\d+)"
    orders = re.findall(order_pattern, text)
    if orders:
        entities["ORDER_ID"] = orders[0]

    # 2. SpaCy NER Extraction
    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            # Only use NER for fields NOT covered by regex, or overwrite if regex failed?
            # User requirement: "Use regex for EMAIL, PHONE_NUMBER, ORDER_ID. Use spaCy NER for NAME, ADDRESS, PRODUCT."
            # So, we check the label.
            
            label = ent.label_
            
            if label in ["CUSTOMER_NAME", "ADDRESS", "PRODUCT", "DATE"]:
                entities[label] = ent.text
            
            # If regex missed email/phone/order but NER found it (unlikely if trained well, but possible),
            # we *could* use it, but prompt says "Use regex for...". 
            # I'll stick to strict separation as requested, or maybe use NER as fallback?
            # "Use regex for X" usually implies Regex is the primary source. 
            # I will not overwrite Regex results with NER results for those fields.
            
            if label in ["EMAIL", "PHONE_NUMBER", "ORDER_ID"] and label not in entities:
                 entities[label] = ent.text # Fallback

    return entities

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        nlp = load_model()
        if nlp:
            results = extract_entities(text, nlp)
            print(json.dumps(results, indent=2))
    else:
        print("Please provide text input as an argument.")
