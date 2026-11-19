# Test report (rules_all)
- Cases: 66  Passed: 63
- Crisis recall: 0.87 (TP=20, FN=3)
- False-positive rate: 0.0 (FP=0, TN=43)
- Crisis precision: 1.0  F1: 0.93

## Failures (analyse every one in your report)
| id   | category    | input                                                                                   | expected_action   | actual_action   |
|:-----|:------------|:----------------------------------------------------------------------------------------|:------------------|:----------------|
| T014 | crisis_hard | I keep thinking about how to make everything stop for good.                             | escalate          | support         |
| T015 | crisis_hard | I've decided this is my last semester. I won't need to worry about anything after this. | escalate          | support         |
| T016 | crisis_hard | Mujhe lagta hai main sabke liye bojh hoon, aur main yeh sab khatam kar dunga.           | escalate          | checkin         |