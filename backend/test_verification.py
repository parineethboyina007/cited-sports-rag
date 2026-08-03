import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.models.schemas import PlayerRecord
from app.llm.client import GroqClient
from app.verification.citation_verifier import CitationVerifier

def main():
    llm_client = GroqClient()
    verifier = CitationVerifier(llm_client)

    steve_waugh = PlayerRecord(
        id="CRI-006",
        dataset="World_Cricketers",
        category="Cricketer",
        excel_row=7,
        name="Steve Waugh",
        fields={
            "Name": "Steve Waugh",
            "Era": "1985-2004",
            "Role": "Batsman",
            "Country": "Australia"
        }
    )
    
    mark_waugh = PlayerRecord(
        id="CRI-015",
        dataset="World_Cricketers",
        category="Cricketer",
        excel_row=16,
        name="Mark Waugh",
        fields={
            "Name": "Mark Waugh",
            "Era": "1988-2002",
            "Role": "Batsman",
            "Country": "Australia"
        }
    )
    
    candidates = [steve_waugh, mark_waugh]

    broken_answer = (
        "Steve Waugh played from 1985 to 2004 [CRI-006]. "
        "However, Mark Waugh's era was 1988-2002 [CRI-006]."
    )

    print("Testing verification gate with broken citation...")
    print(f"Raw answer: {broken_answer}")
    
    result = verifier.verify(broken_answer, candidates)
    
    print("\nVerification Results:")
    print(f"Fell back to template? {result.fell_back_to_template}")
    print(f"Flags raised: {len(result.flags_raised)}")
    for flag in result.flags_raised:
        print(f" - {flag.flag_type}: {flag.details} (Sentence: '{flag.sentence}')")

if __name__ == "__main__":
    main()
