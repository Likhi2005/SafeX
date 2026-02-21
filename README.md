# SAFEX

Build a lightweight, CPU-only security layer that sits between users and LLMs, detecting and blocking prompt injection, jailbreaks, and context leakage attacks with explainable risk scores.

---

## Workflows

### Creation of Basic Structure of the Project

```bash
python template.py
```

---

## STEP 01 — Create a Conda Environment

After opening the repository:

```bash
conda create -n shieldgpt python=3.10 -y
conda activate shieldgpt
```

---

## STAGE 2 — Regex-Based Jailbreak Filter

Implement the fast, regex-based security filter to catch obvious attacks instantly.

---

## STAGE 3 — Obfuscation Detector

This step is to implement the obfuscation detector that catches sneaky encoding tricks attackers use to bypass regex filters.

---

## STAGE 4 — DistilBERT Classifier for Advanced Attack Detection

This step is to implement the ML-based classifier using DistilBERT for sophisticated attack detection that regex patterns might miss.

---

## STAGE 5 — Policy Engine & Decision Logic

This step is to implement the Policy Engine that combines all filter results and makes final decisions:

- ALLOW  
- SANITIZE  
- BLOCK  

---

## Test Cases

Run individual test files:

```bash
python -m pytest tests/test_regex_filter.py -v
python -m pytest tests/test_obfuscation.py -v
python -m pytest tests/test_ml_classifier.py -v
python -m pytest tests/test_policy_engine.py -v
python -m pytest tests/test_sanitizer.py -v
```

---

### For Multiple Test Cases

```bash
python -m pytest tests/ -v
```