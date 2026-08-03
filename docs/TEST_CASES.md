# Test Cases

The following mandatory test cases are automated in `backend/tests/test_acceptance_suite.py` and run against the live API endpoint.

| # | Query | Required behavior | What it's actually testing |
|---|---|---|---|
| 1 | "How many Olympic medals has Neeraj Chopra won, and where?" | Cites [OLY-001]; Gold@Tokyo 2020 + Silver@Paris 2024, correctly paired | Baseline multi-medal correctness |
| 2 | "Tell me about Khan." | Lists all 4 — Zaheer [CRI-040], Imran [CRI-063], Younis [CRI-070], Rashid [CRI-126] — as distinct people, never merged | 4-way surname collision, 3 countries |
| 3 | "Compare Steve Waugh and Mark Waugh." | CRI-006 (1985–2004) vs CRI-015 (1988–2002) kept strictly separate; eras/achievements not swapped | Twin siblings — hardest case in the set |
| 4 | "What did Shahid Afridi and Shaheen Afridi each achieve?" | CRI-068 (all-rounder, 1996–2018) vs CRI-078 (bowler, 2018–present), correctly attributed | Same surname, same country, different generation |
| 5 | "Tell me about Kumar." | Kumar Sangakkara [CRI-080, cricket] + Sushil Kumar [OLY-006], Ravi Kumar Dahiya [OLY-012], Vijay Kumar [OLY-015] — 4 people, 2 files, clearly separated | The core multi-document / cross-dataset test |
| 6 | "Tell me about Singh." | All 5 — 3 cricketers [CRI-037, CRI-041, CRI-042] + 2 Olympians [OLY-019, OLY-022] — listed distinctly, including the middle-token match (Bishan Singh **Bedi**) | Largest collision; tests token matching isn't first-token-only |
| 7 | "What is Rafael Nadal's Olympic medal record?" | Clean refusal — Nadal is in neither dataset | No-source refusal, absent entity |
| 8 | "What is Virat Kohli's net worth?" | Refuses / states the datasets don't track this, even though Virat Kohli [CRI-026] exists | Entity present, attribute absent — the tempting-to-fabricate case |
| 9 | "What was Sachin Tendulkar's highest individual Test score?" | Refuses / not recorded — [CRI-025]'s Background doesn't contain that figure, even though it's true and well-known | Resistance to parametric-knowledge leakage |
| 10 | "List all Sri Lankan wicket-keeper batsmen in the dataset." | Returns Kumar Sangakkara [CRI-080] only — verified as the sole match | Structured-field filter correctness |
| 11 | "Which Olympic athlete competed at both Beijing 2008 and London 2012?" | Sushil Kumar [OLY-006]; Bronze↔Beijing 2008, Silver↔London 2012, not swapped | Standard 1:1 positional pairing |
| 12 | "How many medals did Manu Bhaker win at Paris 2024, and what color?" | [OLY-004]: two bronze medals, both at Paris 2024 (not "one bronze") | The irregular pairing case — single Games, multiple medals |
