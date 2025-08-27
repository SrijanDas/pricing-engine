# Donizo Pricing Engine

A pricing engine for bathroom renovations that transforms voice transcripts into structured, professional renovation quotes.

## Features

-   Voice transcript analysis using OpenAI GPT
-   Modular pricing system with material costs, labor calculations, and VAT rules
-   Confidence scoring for pricing accuracy

## Quick Start

### Prerequisites

-   Python 3.8+
-   OpenAI API key

### Installation

1. Clone the repository:

```bash
git clone <your-repo>
cd donizo-pricing-engine
```

2. Install dependencies using uv:

```bash
uv sync
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Usage

```bash
# Run the pricing engine
uv run python main.py
```

## Output Schema

The system generates quotes following this structure:

```json
{
    "quote_id": "unique_identifier",
    "client_location": "city_name",
    "project_summary": "description",
    "zones": {
        "bathroom": {
            "tasks": [
                {
                    "name": "task_name",
                    "labor": { "hours": 8, "rate": 45, "total": 360 },
                    "materials": [
                        {
                            "name": "item",
                            "quantity": 10,
                            "unit_price": 25,
                            "total": 250
                        }
                    ],
                    "vat_rate": 0.2,
                    "estimated_duration": "1-2 days",
                    "subtotal": 610,
                    "vat_amount": 122,
                    "total_price": 732,
                    "margin": 0.15,
                    "confidence_score": 0.85
                }
            ]
        }
    },
    "global_confidence_score": 0.82,
    "total_before_vat": 5000,
    "total_vat": 1000,
    "grand_total": 6000
}
```

## Pricing Logic

### Material Costs

-   Database of standard materials with base prices
-   Supplier markup (5-15% depending on availability)

### Labor Calculations

-   Skilled vs. unskilled hourly rates
-   Task complexity multipliers

### VAT Rules

-   Standard rate: 20%
-   Reduced rate: 10% for renovation work (under certain conditions)
-   Zero rate: 0% for specific accessibility improvements

### Margin Protection

-   Minimum 15% margin on all quotes
-   Risk adjustment based on project complexity
-   Confidence-based margin scaling

## Confidence Scoring

The system evaluates quote reliability based on:

-   Input clarity (0.0-1.0)
-   Material availability (0.0-1.0)
-   Labor estimate accuracy (0.0-1.0)
-   Market price stability (0.0-1.0)

**Confidence Levels:**

-   0.9-1.0: Very High (ready to quote)
-   0.8-0.89: High (minor clarifications needed)
-   0.7-0.79: Medium (requires review)
-   0.6-0.69: Low (needs significant input)
-   <0.6: Very Low (insufficient data)

## Future Enhancements

-   Track accepted/rejected quotes for model refinement
-   Real-time material pricing integration
