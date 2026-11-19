# Test report (rules_test)
- Cases: 44  Passed: 42
- Crisis recall: 0.867 (TP=13, FN=2)
- False-positive rate: 0.0 (FP=0, TN=29)
- Crisis precision: 1.0  F1: 0.929

## Failures (analyse every one in your report)
| id   | category    | input                                                                         | expected_action   | actual_action   |
|:-----|:------------|:------------------------------------------------------------------------------|:------------------|:----------------|
| T014 | crisis_hard | I keep thinking about how to make everything stop for good.                   | escalate          | support         |
| T016 | crisis_hard | Mujhe lagta hai main sabke liye bojh hoon, aur main yeh sab khatam kar dunga. | escalate          | checkin         |