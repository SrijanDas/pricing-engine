# Donizo Pricing Engine

A pricing engine for bathroom renovations that transforms voice transcripts into structured, professional renovation quotes.

## Features

-   Voice transcript analysis using OpenAI GPT
-   Modular pricing system with material costs, labor calculations, and VAT rules
-   Confidence scoring

## Quick Start

### Prerequisites

-   Python 3.8+
-   OpenAI API key

### Installation

1. Clone the repository:

```bash
git clone https://github.com/SrijanDas/pricing-engine
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

## Pricing Logic

The system calculates renovation costs using four main components that work together to produce accurate quotes.

### Material Costs

The system maintains a comprehensive database of bathroom renovation materials including tiles, plumbing fixtures, electrical components, and consumables. Each material has:

-   Mock data for material prices can be found in `src\pricing\material_db.py`
-   Different quality variants (basic, premium, luxury) with appropriate pricing multipliers
-   Availability scores that reflect current market conditions
-   Coverage calculations to determine exact quantities needed

The system automatically selects materials based on the customer's budget preference and calculates quantities based on room dimensions.

### Labor Calculations

Labor costs are calculated using a sophisticated hourly rate system:

-   Four skill levels: Unskilled (25€/hr), Semi-skilled (35€/hr), Skilled (45€/hr), Specialist (65€/hr)
-   Task-specific time estimates based on industry standards
-   Complexity multipliers that adjust time estimates based on project difficulty
-   OpenAI integration to automatically classify tasks into appropriate categories

For example, tiling work uses skilled labor at 45€/hr with 2.5 hours per square meter as the base rate, then applies complexity multipliers.

### VAT Rules (French Tax System)

The system automatically applies the correct French VAT rates based on work type:

| **Type of Work**                                   | **VAT Rate** | **Conditions**                                    |
| -------------------------------------------------- | ------------ | ------------------------------------------------- |
| New construction, extensions, non-residential work | 20%          | Standard rate applies                             |
| Renovation, maintenance, transformation (home >2y) | 10%          | Reduced rate for existing homes                   |
| Energy-efficiency renovation (insulation, heating) | 5.5%         | Requires certified equipment and VAT certificates |
| Gas/oil boiler installation (from 2025)            | 20%          | Standard rate even for energy-efficiency projects |

### Margin Protection

The system ensures profitability through dynamic margin calculations:

-   Base margin of 15% on all quotes (industry minimum)
-   Complexity adjustments: Simple (0%), Moderate (+2%), Complex (+5%)
-   Budget-based adjustments: Budget-conscious (-2%), Premium (+5%), Luxury (+10%)
-   Final margins are capped between 15% and 30% to remain competitive

## Confidence Scoring System

The confidence scoring system evaluates how reliable each quote is by analyzing multiple factors and producing a score from 0.0 to 1.0.

### How Confidence is Calculated

The system uses three weighted components:

-   **Input Clarity (40% weight)**: How clear and complete the project requirements are
-   **Material Availability (30% weight)**: Current availability and price stability of required materials
-   **Labor Accuracy (30% weight)**: How well the labor estimates match the actual work needed

### Input Clarity Scoring

This measures how well we understand what the customer wants:

-   Room dimensions provided: adds clarity
-   Clear task descriptions: improves score
-   Budget information specified: reduces uncertainty
-   Timeline requirements: helps with planning
-   Material preferences: enables better matching

### Material Availability Scoring

This evaluates supply chain reliability:

-   Current supplier stock levels
-   Price stability over recent months
-   Supplier reliability ratings
-   Seasonal availability factors

### Labor Accuracy Scoring

This assesses how confident we are in our time estimates:

-   Task standardization: how common/routine the work is
-   Complexity assessment accuracy: how well we understand difficulty
-   Local labor data availability: access to regional rates
-   Skill requirement clarity: understanding what expertise is needed

### Confidence Levels and Actions

The final confidence score determines how to proceed:

-   **0.9-1.0 Very High**: Quote is ready to send, high accuracy expected
-   **0.8-0.89 High**: Minor clarifications may be needed, generally reliable
-   **0.7-0.79 Medium**: Review recommended, add 5-10% contingency
-   **0.6-0.69 Low**: Detailed review required, consider site visit
-   **Below 0.6 Very Low**: Do not quote without additional information

## Future Enhancements

-   Track accepted/rejected quotes for model refinement
-   Real-time material pricing integration
