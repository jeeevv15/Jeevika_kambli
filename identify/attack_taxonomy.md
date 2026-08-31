# GenAI-Powered Payment Fraud — Attack Taxonomy

67 attack vectors across 15 categories, spanning identity, social engineering,
transaction rails, merchant infrastructure, device/malware, automation, and the
AI/ML systems that now sit inside the payment stack itself.

Each entry is grounded in documented fraud patterns (card networks' fraud
reporting, EPC/ECB payment-fraud advisories, Europol financial-crime reporting)
and describes how GenAI specifically changes the attack's speed, scale, or
fidelity relative to its pre-GenAI form.

Categories marked **[SIMULATED]** have a corresponding generator in
`generate/simulators/` and are actively detected and evaluated in this repo's
closed loop. All others are documented here for completeness of the threat
landscape (breadth of "Identify") but are not separately built.

---

## A. Identity & Onboarding Fraud
1. Synthetic identity fraud — GenAI-fabricated identity + document bundles
2. Deepfake video KYC bypass — face-swap liveness spoofing
3. AI-cloned voice biometric bypass
4. Synthetic financial documents (fake pay stubs/bank statements)

## B. Social Engineering / Authorization Fraud
5. Deepfake voice vishing ("this is your bank/CEO, authorize this transfer")
6. LLM-generated hyper-personalized phishing/smishing at scale
7. AI-powered romance / pig-butchering scam scripts leading to payment coercion
8. Fake AI customer-support chatbots harvesting card/OTP data
9. Deepfake CEO/executive fraud for wire authorization (BEC 2.0)

## C. Transaction & Card Abuse **[SIMULATED]**
10. Automated LLM-assisted card testing / carding — `card_abuse_sim.py`
11. AI-generated fake merchant storefronts (card-not-present fraud)
12. Triangulation fraud via AI-run fake e-commerce sites
13. OTP-bot automation — real-time OTP phishing bots

## D. Adversarial-ML Attacks **[SIMULATED]**
14. Low-and-slow transactions engineered under detection thresholds — `adversarial_ml_sim.py`
15. Adversarial perturbation of transaction features to evade a known classifier
16. Prompt injection against AI banking/support agents to trigger unauthorized transactions
17. LLM-coordinated mule account networks

## E. Account Takeover **[SIMULATED]**
18. Credential-stuffing + AI behavioral mimicry post-ATO — `ato_sim.py`
19. AI-assisted SIM-swap coordination for OTP interception
20. AI-generated fake dispute/chargeback narratives (friendly fraud at scale)

## F. Payment-Rail / Transaction Manipulation
21. QR-code payment redirection fraud
22. QR-code replacement / "quishing" campaigns
23. Verification-of-Payee / beneficiary deception
24. AI-generated Request-to-Pay manipulation
25. Instant-payment scam escalation
26. Payment-link hijacking / replacement

## G. Merchant-Side Fraud
27. AI-created fraudulent merchant identity
28. Merchant collusion / transaction laundering
29. Merchant account takeover
30. AI-generated fake reviews / reputation manipulation
31. Merchant payout / settlement-account manipulation
32. Transaction laundering through benign merchants

## H. Refund, Chargeback & Post-Purchase Abuse
33. AI-generated refund abuse
34. Refund routing manipulation
35. Friendly-fraud behavioral simulation
36. Policy-abuse optimization
37. Multi-channel chargeback abuse

## I. Malware / Device-Level Payment Fraud
38. AI-assisted banking malware with adaptive behavior
39. Mobile overlay fraud
40. AI-driven remote-access fraud
41. Device fingerprint mimicry
42. Session-hijacking with behavioral imitation

## J. Bot / Automation Fraud **[SIMULATED]**
43. AI-adaptive payment bots — `bot_automation_sim.py`
44. Distributed low-volume fraud
45. Coordinated botnet transaction campaigns
46. AI-generated behavioral camouflage
47. Fraud velocity adaptation (dynamically slows when flagged)

## K. Cross-Channel / Multi-Stage Fraud
48. Cross-channel identity takeover (social media → email → mobile → payment)
49. Multi-stage fraud orchestration (recon → engineering → auth compromise → payment → laundering)
50. AI-generated "fraud journey" attacks — agent adapts to victim's response
51. Cross-account coordinated fraud
52. Customer-support escalation manipulation

## L. Data / Intelligence Poisoning **[SIMULATED]**
53. Fraud-model data poisoning — `poisoning_sim.py`
54. Feedback-loop poisoning (false labels corrupt future model behavior)
55. Behavioral baseline poisoning (suspicious behavior absorbed into "normal")
56. Synthetic identity network contamination

## M. AI-Agent / LLM Infrastructure Attacks
57. Tool-use manipulation against financial AI agents
58. Retrieval poisoning against fraud/support AI
59. Agent identity impersonation
60. Multi-agent fraud coordination

## N. Investment / Scam Payment Fraud
61. AI-generated investment scam ecosystems
62. AI-generated fake financial advisors
63. Synthetic proof-of-payment / proof-of-return

## O. Telecom / Communication-Layer Fraud
64. Caller-ID impersonation
65. AI-generated voicemail impersonation
66. Communication-channel switching attack
67. AI-generated bank-alert impersonation

---

## Why these 5 families were chosen for deep simulation

The closed loop needs attack families that (a) express themselves in
transaction-level data with real fidelity, (b) benefit from a multi-round
adversarial loop (i.e. the attacker can meaningfully adapt), and (c) span
different detection layers so the ensemble's breadth is actually tested:

- **Card Abuse** → tests raw transaction-pattern detection (velocity, amount, merchant risk)
- **Account Takeover** → tests behavioral-deviation detection (session/device drift from a known baseline)
- **Bot/Automation** → tests adaptive-adversary detection (the attacker changes tactics mid-loop)
- **Adversarial-ML** → tests the detector's own robustness (attacks the model, not the payment)
- **Poisoning** → tests the training pipeline's integrity (attacks the *defense*, not any single transaction)

Together these five stress every layer of the system described in the
Defend + Observability modules, while the remaining 62 attacks are documented
here to demonstrate full landscape awareness.
