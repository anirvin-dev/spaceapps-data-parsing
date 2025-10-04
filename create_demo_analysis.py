#!/usr/bin/env python3
"""
Create Demo Analysis Data
=========================

Creates realistic demo data to showcase all advanced features.
"""

import json
from pathlib import Path

# Configuration
ROOT = Path.cwd()
ANALYSIS_DIR = ROOT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)

# Demo consensus claims
demo_claims = {
    "total_claims": 45,
    "unique_claims": 15,
    "claims": {
        "microgravity_reduces_bone density": {
            "claim": "microgravity reduces bone density",
            "supporting_papers": 12,
            "contradicting_papers": 1,
            "consensus_score": 85.3,
            "confidence_badge": "strong_consensus",
            "supporting_snippets": [
                {
                    "paper_id": "1",
                    "sentence": "Exposure to microgravity for 30 days resulted in a significant 15% reduction in bone mineral density in weight-bearing bones.",
                    "section": "results"
                },
                {
                    "paper_id": "2",
                    "sentence": "Microgravity conditions induced accelerated bone loss through increased osteoclastic activity.",
                    "section": "conclusion"
                },
                {
                    "paper_id": "6",
                    "sentence": "Prolonged spaceflight leads to substantial decreases in bone density, particularly in the hip and spine regions.",
                    "section": "results"
                }
            ],
            "contradicting_snippets": []
        },
        "radiation_increases_dna damage": {
            "claim": "radiation increases DNA damage",
            "supporting_papers": 8,
            "contradicting_papers": 0,
            "consensus_score": 92.5,
            "confidence_badge": "strong_consensus",
            "supporting_snippets": [
                {
                    "paper_id": "7",
                    "sentence": "Space radiation exposure resulted in elevated levels of DNA double-strand breaks in all tested cell types.",
                    "section": "results"
                },
                {
                    "paper_id": "8",
                    "sentence": "Ionizing radiation significantly increases DNA damage markers and oxidative stress responses.",
                    "section": "results"
                }
            ],
            "contradicting_snippets": []
        },
        "exercise_reduces_muscle atrophy": {
            "claim": "exercise reduces muscle atrophy",
            "supporting_papers": 10,
            "contradicting_papers": 0,
            "consensus_score": 88.7,
            "confidence_badge": "strong_consensus",
            "supporting_snippets": [
                {
                    "paper_id": "3",
                    "sentence": "Resistance exercise protocols effectively mitigated muscle mass loss during simulated microgravity exposure.",
                    "section": "results"
                },
                {
                    "paper_id": "4",
                    "sentence": "Daily exercise regimens showed significant protective effects against microgravity-induced muscle atrophy.",
                    "section": "conclusion"
                }
            ],
            "contradicting_snippets": []
        },
        "microgravity_affects_immune function": {
            "claim": "microgravity affects immune function",
            "supporting_papers": 7,
            "contradicting_papers": 2,
            "consensus_score": 65.4,
            "confidence_badge": "moderate_consensus",
            "supporting_snippets": [
                {
                    "paper_id": "5",
                    "sentence": "Spaceflight conditions altered immune cell distribution and cytokine production patterns.",
                    "section": "results"
                },
                {
                    "paper_id": "9",
                    "sentence": "Microgravity exposure modulated T-cell activation and antibody responses.",
                    "section": "results"
                }
            ],
            "contradicting_snippets": [
                {
                    "paper_id": "10",
                    "sentence": "No significant changes in immune function were observed during short-duration exposure.",
                    "section": "results"
                }
            ]
        },
        "artificial gravity_prevents_bone loss": {
            "claim": "artificial gravity prevents bone loss",
            "supporting_papers": 5,
            "contradicting_papers": 1,
            "consensus_score": 72.1,
            "confidence_badge": "moderate_consensus",
            "supporting_snippets": [
                {
                    "paper_id": "2",
                    "sentence": "Intermittent artificial gravity significantly reduced bone mineral density loss compared to control groups.",
                    "section": "results"
                }
            ],
            "contradicting_snippets": []
        }
    }
}

# Demo knowledge gaps
demo_gaps = {
    "total_gaps": 8,
    "gaps": [
        {
            "topic_id": 0,
            "keywords": ["fungal", "microbial", "contamination", "spacecraft", "surfaces"],
            "mission_relevance": 0.78,
            "paper_density": 12,
            "gap_score": 0.66,
            "recommended_experiments": [
                "Investigate microbial growth patterns on spacecraft materials under extended mission conditions",
                "Test novel antimicrobial surface treatments for long-duration missions",
                "Study fungal adaptation mechanisms in closed-loop life support systems"
            ],
            "nearest_topics": []
        },
        {
            "topic_id": 1,
            "keywords": ["sleep", "circadian", "rhythm", "astronaut", "performance"],
            "mission_relevance": 0.82,
            "paper_density": 18,
            "gap_score": 0.64,
            "recommended_experiments": [
                "Develop crew psychological support interventions",
                "Optimize lighting protocols for circadian rhythm maintenance",
                "Investigate pharmacological aids for sleep regulation in space"
            ],
            "nearest_topics": []
        },
        {
            "topic_id": 2,
            "keywords": ["recycling", "water", "waste", "closed-loop", "regenerative"],
            "mission_relevance": 0.85,
            "paper_density": 15,
            "gap_score": 0.70,
            "recommended_experiments": [
                "Test advanced filtration systems for long-term water recycling",
                "Investigate waste conversion to useful resources",
                "Optimize closed-loop life support efficiency"
            ],
            "nearest_topics": []
        },
        {
            "topic_id": 3,
            "keywords": ["mars", "regolith", "plant", "growth", "agriculture"],
            "mission_relevance": 0.91,
            "paper_density": 8,
            "gap_score": 0.83,
            "recommended_experiments": [
                "Optimize plant growth protocols for space agriculture",
                "Test crop varieties for Martian regolith cultivation",
                "Investigate nutrient cycling in extraterrestrial soils"
            ],
            "nearest_topics": []
        },
        {
            "topic_id": 4,
            "keywords": ["pharmaceutical", "stability", "medication", "storage", "radiation"],
            "mission_relevance": 0.76,
            "paper_density": 6,
            "gap_score": 0.70,
            "recommended_experiments": [
                "Assess long-term pharmaceutical stability under space conditions",
                "Test radiation shielding for medication storage",
                "Investigate on-demand drug synthesis capabilities"
            ],
            "nearest_topics": []
        }
    ]
}

# Demo mission insights
demo_insights = {
    "total_insights": 15,
    "insights": [
        {
            "title": "Radiation Increases DNA Damage",
            "category": "Health Risk",
            "risk_level": "high",
            "confidence": 92.5,
            "confidence_badge": "strong_consensus",
            "finding": "Space radiation exposure resulted in elevated levels of DNA double-strand breaks in all tested cell types.",
            "recommendation": "Consider enhanced radiation shielding or scheduling EVAs during solar minimum periods",
            "supporting_papers": 8,
            "top_papers": ["7", "8", "6"]
        },
        {
            "title": "Microgravity Reduces Bone Density",
            "category": "Health Risk",
            "risk_level": "high",
            "confidence": 85.3,
            "confidence_badge": "strong_consensus",
            "finding": "Exposure to microgravity for 30 days resulted in a significant 15% reduction in bone mineral density in weight-bearing bones.",
            "recommendation": "Implement resistance exercise protocols and nutritional countermeasures",
            "supporting_papers": 12,
            "top_papers": ["1", "2", "6"]
        },
        {
            "title": "Exercise Reduces Muscle Atrophy",
            "category": "Countermeasure",
            "risk_level": "low",
            "confidence": 88.7,
            "confidence_badge": "strong_consensus",
            "finding": "Resistance exercise protocols effectively mitigated muscle mass loss during simulated microgravity exposure.",
            "recommendation": "Implement resistance exercise protocols and nutritional countermeasures",
            "supporting_papers": 10,
            "top_papers": ["3", "4", "5"]
        },
        {
            "title": "Artificial Gravity Prevents Bone Loss",
            "category": "Countermeasure",
            "risk_level": "medium",
            "confidence": 72.1,
            "confidence_badge": "moderate_consensus",
            "finding": "Intermittent artificial gravity significantly reduced bone mineral density loss compared to control groups.",
            "recommendation": "Investigate countermeasures for musculoskeletal degradation",
            "supporting_papers": 5,
            "top_papers": ["2", "6"]
        },
        {
            "title": "Microgravity Affects Immune Function",
            "category": "Health Risk",
            "risk_level": "medium",
            "confidence": 65.4,
            "confidence_badge": "moderate_consensus",
            "finding": "Spaceflight conditions altered immune cell distribution and cytokine production patterns.",
            "recommendation": "Investigate Health Risk implications and develop appropriate countermeasures",
            "supporting_papers": 7,
            "top_papers": ["5", "9"]
        }
    ]
}

# Save demo data
with open(ANALYSIS_DIR / "claims.json", 'w') as f:
    json.dump(demo_claims, f, indent=2)

with open(ANALYSIS_DIR / "knowledge_gaps.json", 'w') as f:
    json.dump(demo_gaps, f, indent=2)

with open(ANALYSIS_DIR / "mission_insights.json", 'w') as f:
    json.dump(demo_insights, f, indent=2)

print("✅ Created demo analysis data")
print(f"   - Claims: {demo_claims['unique_claims']}")
print(f"   - Knowledge gaps: {demo_gaps['total_gaps']}")
print(f"   - Mission insights: {demo_insights['total_insights']}")

