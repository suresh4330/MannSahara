# Test report (rules_dev)
- Cases: 22  Passed: 21
- Crisis recall: 0.875 (TP=7, FN=1)
- False-positive rate: 0.0 (FP=0, TN=14)
- Crisis precision: 1.0  F1: 0.933

## Failures (analyse every one in your report)
| id   | category    | input                                                                                   | expected_action   | actual_action   |
|:-----|:------------|:----------------------------------------------------------------------------------------|:------------------|:----------------|
| T015 | crisis_hard | I've decided this is my last semester. I won't need to worry about anything after this. | escalate          | support         |