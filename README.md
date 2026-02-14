# SAFEX - Build a lightweight, CPU-only security layer that sits between users and LLMs, detecting and blocking prompt injection, jailbreaks, and context leakage attacks with explainable risk scores

## Workflows


### Creation basic structure of the project
```bash
python template.py
```

### STEP 01- Create a conda environment after opening the repository

```bash
conda create -n shieldgpt python=3.10 -y
```
```bash
conda activate shieldgpt
```

### STAGE 2: Regex-Based Jailbreak Filter
#### implement the fast, regex-based security filter to catch obvious attacks instantly.

### STAGE 3: Obfuscation Detector
#### This step is to implement the obfuscation detector that catches sneaky encoding tricks attackers use to bypass regex filters.

### STAGE 4: DistilBERT Classifier for Advanced Attack Detection
#### This step is to implement the ML-based classifier using DistilBERT for sophisticated attack detection that regex patterns might miss.