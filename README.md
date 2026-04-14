# Customer Named Entity Recognition using spaCy

This project implements a hybrid Named Entity Recognition (NER) system using spaCy and Regex to extract customer-related entities from text.

## Project Structure

```
/data           - Generated training data
/model          - Saved spaCy model
/training       - (Optional)
/inference      - (Optional)
annotations.py  - Generates synthetic training data
train.py        - Trains the spaCy NER model
predict.py      - Runs inference using Model + Regex
requirements.txt- Project dependencies
README.md       - Project documentation
```

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm # Optional base model
    ```

2.  **Generate Data**:
    ```bash
    python annotations.py
    ```
    Creates `data/training_data.json`.

## Usage

### Training

```bash
python train.py
```
Trains the model for 20 epochs and saves it to `model/`.

### Inference

```bash
python predict.py "Hi, this is John Doe. My order OD12345 hasn't arrived. Email: john@email.com"
```

**Output:**
```json
{
  "CUSTOMER_NAME": "John Doe",
  "ORDER_ID": "OD12345",
  "EMAIL": "john@email.com"
}
```

## Logic

- **Regex**: Extracts `EMAIL`, `PHONE_NUMBER`, `ORDER_ID` for high precision.
- **SpaCy NER**: Extracts `CUSTOMER_NAME`, `ADDRESS`, `PRODUCT`, `DATE` based on context.
