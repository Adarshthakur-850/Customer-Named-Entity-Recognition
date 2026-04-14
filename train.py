
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
import json
import os

def load_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} training examples.")
    return data

def train_model(training_data, n_iter=20, model_dir="model"):
    # Create a blank 'en' model
    nlp = spacy.blank("en")
    print("Created blank 'en' model")

    # Create the NER component and add it to the pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # Add labels
    for _, annotations in training_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Disable other pipes during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    
    # Split data into train and dev (80/20)
    random.shuffle(training_data)
    train_size = int(len(training_data) * 0.8)
    train_data = training_data[:train_size]
    dev_data = training_data[train_size:]
    
    print(f"Training on {len(train_data)} examples, evaluating on {len(dev_data)} examples")

    with nlp.select_pipes(disable=other_pipes):
        optimizer = nlp.begin_training()
        
        for itn in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            
            # Create batches
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            
            for batch in batches:
                texts, annotations = zip(*batch)
                
                examples = []
                for i in range(len(texts)):
                    doc = nlp.make_doc(texts[i])
                    try:
                        example = Example.from_dict(doc, annotations[i])
                        examples.append(example)
                    except Exception as e:
                        print(f"Skipping bad example: {texts[i]} - {e}")
                
                if examples:
                    nlp.update(
                        examples,
                        drop=0.5,
                        losses=losses,
                    )
            
            print(f"Epoch {itn + 1}: Loss {losses['ner']:.4f}")

    # Evaluation on dev set
    print("\nEvaluating on dev set...")
    scorer = nlp.evaluate([Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in dev_data])
    print("\nEvaluation Results:")
    print(f"Precision: {scorer['ents_p']:.4f}")
    print(f"Recall: {scorer['ents_r']:.4f}")
    print(f"F1-score: {scorer['ents_f']:.4f}")

    # Save model
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    nlp.to_disk(model_dir)
    print(f"Saved model to {model_dir}")

if __name__ == "__main__":
    data_path = "data/training_data.json"
    if os.path.exists(data_path):
        data = load_data(data_path)
        # Convert list of lists to list of tuples if needed, though json load returns lists
        # spacy expects tuples generally but list is fine for iteration, but let's be safe
        formatted_data = []
        for text, annot in data:
            formatted_data.append((text, annot))
            
        train_model(formatted_data)
    else:
        print(f"Data file not found at {data_path}. Please run annotations.py first.")
