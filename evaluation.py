import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from bert_score import score

def evaluate_with_bert_score(candidate, reference):
    """Calculate BERTScore between a candidate answer and a reference answer."""
    P, R, F1 = score([candidate], [reference], lang="en", verbose=True)
    return {
        "Precision": P.mean().item(),
        "Recall": R.mean().item(),
        "F1 Score": F1.mean().item()
    }

def evaluate_with_glue_sts(sentence1, sentence2):
    """Calculate GLUE STS score between two sentences."""
    model_name = "sentence-transformers/stsb-roberta-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    inputs = tokenizer(sentence1, sentence2, return_tensors="pt")
    with torch.no_grad():
        scores = model(**inputs).logits

    sts_score = torch.sigmoid(scores).item() * 5
    return sts_score

if __name__ == "__main__":
    # Example test cases
    # candidate_answer = "Tesla Model 3's battery is 82 kWh."
    #candidate_answer = "The real range of the Tesla Model 3 varies based on weather conditions. In cold weather, the ranges are as follows: - City: 485 km - Highway: 380 km - Combined: 435 km In mild weather conditions, the ranges are significantly higher: - City: 765 km - Highway: 505 km - Combined: 615 km Overall, the range can be between 380 km and 765 km depending on these conditions."
    #candidate_answer = "Price -United Kingdom	Not Available -The Netherlands	€69,990 -Germany	€69,020"
    candidate_answer = """Battery
Nominal Capacity	82.0 kWh
Battery Type	Lithium-ion
Number of Cells	288
Architecture	400 V
Warranty Period	No Data
Warranty Mileage	No Data
Useable Capacity	77.0 kWh
Cathode Material	No Data
Pack Configuration	96s3p
Nominal Voltage	352 V
Form Factor	No Data
Name / Reference	No Data
Battery
Nominal Capacity	82.0 kWh
Battery Type	Lithium-ion
Number of Cells	288
Architecture	400 V
Warranty Period	No Data
Warranty Mileage	No Data
Useable Capacity	77.0 kWh
Cathode Material	No Data
Pack Configuration	96s3p
Nominal Voltage	352 V
Form Factor	No Data
Name / Reference	No Data"""
    reference_answer = "The Volkswagen ID.4 Pro is equipped with a lithium-ion battery that has a nominal capacity of 82.0 kWh. This battery consists of 288 cells and operates on a 400 V architecture. The usable capacity of the battery is 77.0 kWh, and it has a nominal voltage of 352 V. The pack configuration is 96s3p, which indicates the arrangement of the cells within the battery pack. The specifics regarding the warranty period, warranty mileage, cathode material, and form factor of the battery are not available."
    #reference_answer = "The pricing information for the vehicle is as follows: in The Netherlands, the price is €69,990, while in Germany, it is €69,020. There is no pricing information available for the United Kingdom."
    #reference_answer = "Real Range between 380 - 765 km City - Cold Weather	485 km Highway - Cold Weather	380 km Combined - Cold Weather	435 km City - Mild Weather	765 km Highway - Mild Weather	505 km Combined - Mild Weather	615 km"

    # Compute BERTScore
    bert_results = evaluate_with_bert_score(candidate_answer, reference_answer)
    print("BERTScore Results:", bert_results)
