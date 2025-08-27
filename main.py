"""
Entry point for the Donizo pricing engine.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from src.engine import DonizoPricingEngine


def main():
    """Main function."""

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("The engine will use fallback analysis instead of OpenAI.")
        print("To use OpenAI, set your API key in a .env file.")
        print()

    print("Initializing Donizo Pricing Engine...")

    engine = DonizoPricingEngine()
    print("Engine initialized successfully!")
    print()

    sample_transcript = """Client wants to renovate a small 4sqm bathroom. They'll remove the old tiles, 
    redo the plumbing for the shower, replace the toilet, install a vanity, repaint the walls, 
    and lay new ceramic floor tiles. Budget-conscious. Located in Marseille."""

    print("Processing sample transcript:")
    print(f"   '{sample_transcript}'")
    print()

    print("Generating structured quote...")
    quote = engine.generate_quote_from_transcript(sample_transcript)
    print("Quote generated successfully!")
    print()

    summary = engine.get_quote_summary(quote)
    print("Quote Summary:")
    print(f"   Quote ID: {summary['quote_id'][:8]}...")
    print(f"   Location: {summary['location']}")
    print(f"   Total Price: {summary['total']:.2f}€")
    print(f"   Confidence Score: {summary['confidence']:.2f}")
    print(f"   Risk Level: {summary['risk_level']}")
    print(f"   Tasks: {summary['task_count']} identified")
    print()

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "sample_quote.json"

    print("Saving quote to output/sample_quote.json...")

    quote_dict = quote.model_dump()

    quote_dict["created_at"] = quote_dict["created_at"].isoformat()

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(quote_dict, f, indent=2, ensure_ascii=False)

    print(f"Quote saved to {output_file}")
    print()

    print("Detailed Breakdown:")
    for zone_name, zone in quote.zones.items():
        print(f"   Zone: {zone_name.title()} ({zone.area}sqm)")
        for task in zone.tasks:
            print(
                f"     • {task.name}: {task.total_price:.2f}€ (confidence: {task.confidence_score:.2f})")

    print()
    print(f"   Subtotal (before VAT): {quote.total_before_vat:.2f}€")
    print(f"   VAT: {quote.total_vat:.2f}€")
    print(f"   Grand Total: {quote.grand_total:.2f}€")

    print("Donizo Pricing Engine demo completed successfully!")
    print("Check the output/sample_quote.json file for the complete structured quote.")


if __name__ == "__main__":
    main()
