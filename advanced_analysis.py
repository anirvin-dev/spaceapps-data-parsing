#!/usr/bin/env python3
"""
Advanced Analysis Module - Consensus, Claims, Knowledge Gaps
============================================================

This module provides:
- Claim extraction from scientific text
- Consensus scoring across papers
- Knowledge gap detection
- Mission-relevant insights generation
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import logging

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Configuration
ROOT = Path.cwd()
TEXT_DIR = ROOT / "paper_text"
SUM_EX_DIR = ROOT / "summaries" / "extractive"
ANALYSIS_DIR = ROOT / "analysis"
CLAIMS_JSON = ANALYSIS_DIR / "claims.json"
GAPS_JSON = ANALYSIS_DIR / "knowledge_gaps.json"
MISSION_JSON = ANALYSIS_DIR / "mission_insights.json"

# Create analysis directory
ANALYSIS_DIR.mkdir(exist_ok=True)

# Mission-relevant keywords
MISSION_KEYWORDS = {
    "health_risk": ["radiation", "bone", "muscle", "cardiovascular", "immune", "dna damage", "cancer", "vision"],
    "life_support": ["oxygen", "water", "food", "plant", "algae", "recycling", "waste"],
    "crew_performance": ["cognition", "psychology", "stress", "sleep", "teamwork", "isolation"],
    "equipment": ["habitat", "spacesuit", "shielding", "life support system", "regenerative"],
    "countermeasure": ["exercise", "nutrition", "medication", "artificial gravity", "protection"]
}

class ClaimExtractor:
    """Extract scientific claims from text using pattern matching."""
    
    # Pattern templates for claim extraction
    PATTERNS = [
        # Causal patterns
        r"([\w\s]{3,30}?)\s+(causes?|leads? to|results? in|induces?|produces?|increases?|decreases?|reduces?|improves?|enhances?)\s+([\w\s]{3,30})",
        # Effect patterns
        r"([\w\s]{3,30}?)\s+(affects?|influences?|modulates?|regulates?|alters?|modifies?|changes?)\s+([\w\s]{3,30})",
        # Association patterns
        r"([\w\s]{3,30}?)\s+(is associated with|correlates? with|relates? to|linked to)\s+([\w\s]{3,30})",
        # Finding patterns
        r"([\w\s]{3,30}?)\s+(showed?|revealed?|demonstrated?|indicated?)\s+([\w\s]{3,30})",
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.PATTERNS]
    
    def extract_from_text(self, text: str, paper_id: str, section: str = "unknown") -> List[Dict]:
        """Extract claims from text."""
        claims = []
        sentences = re.split(r'[.!?]+', text)
        
        for sent_idx, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence.split()) < 5:  # Skip very short sentences
                continue
            
            for pattern in self.compiled_patterns:
                matches = pattern.findall(sentence)
                for match in matches:
                    if len(match) == 3:
                        subject, predicate, obj = match
                        claim = {
                            "paper_id": paper_id,
                            "section": section,
                            "sentence": sentence,
                            "sentence_idx": sent_idx,
                            "subject": subject.strip().lower(),
                            "predicate": predicate.strip().lower(),
                            "object": obj.strip().lower(),
                            "confidence": 0.7,  # Base confidence
                            "normalized_claim": f"{subject.strip().lower()}_{predicate.strip().lower()}_{obj.strip().lower()}"
                        }
                        claims.append(claim)
        
        return claims

class ConsensusAnalyzer:
    """Analyze consensus across multiple papers."""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(embedding_model)
        self.similarity_threshold = 0.75
    
    def compute_consensus(self, claims: List[Dict]) -> Dict[str, Dict]:
        """Compute consensus scores for claims."""
        if not claims:
            return {}
        
        # Group claims by normalized claim
        claim_groups = defaultdict(list)
        for claim in claims:
            norm = claim["normalized_claim"]
            claim_groups[norm].append(claim)
        
        # Compute embeddings for similarity matching
        unique_sentences = list(set(c["sentence"] for c in claims))
        if len(unique_sentences) > 1:
            embeddings = self.model.encode(unique_sentences)
            similarity_matrix = cosine_similarity(embeddings)
        else:
            similarity_matrix = np.array([[1.0]])
        
        # Build consensus data
        consensus_data = {}
        for norm_claim, group in claim_groups.items():
            if len(group) < 2:
                continue  # Need at least 2 papers for consensus
            
            paper_ids = list(set(c["paper_id"] for c in group))
            supporting = len(paper_ids)
            
            # Simple consensus score (can be refined)
            consensus_score = min(100, (supporting / len(claims)) * 100 * 10)
            
            consensus_data[norm_claim] = {
                "claim": f"{group[0]['subject']} {group[0]['predicate']} {group[0]['object']}",
                "supporting_papers": supporting,
                "contradicting_papers": 0,  # Placeholder for contradiction detection
                "consensus_score": round(consensus_score, 1),
                "confidence_badge": self._get_badge(consensus_score, supporting),
                "supporting_snippets": [
                    {
                        "paper_id": c["paper_id"],
                        "sentence": c["sentence"],
                        "section": c["section"]
                    }
                    for c in group[:5]  # Top 5 supporting snippets
                ],
                "contradicting_snippets": [],  # Placeholder
            }
        
        return consensus_data
    
    def _get_badge(self, score: float, count: int) -> str:
        """Determine confidence badge."""
        if count >= 5 and score >= 60:
            return "strong_consensus"
        elif count >= 3 and score >= 40:
            return "moderate_consensus"
        elif count >= 2:
            return "weak_consensus"
        else:
            return "insufficient_evidence"

class KnowledgeGapDetector:
    """Detect knowledge gaps in the literature."""
    
    def __init__(self):
        self.mission_keywords = MISSION_KEYWORDS
    
    def detect_gaps(self, topics: Dict, paper_texts: Dict[str, str]) -> List[Dict]:
        """Detect knowledge gaps."""
        gaps = []
        
        # Analyze topic density
        if not topics or "topics" not in topics:
            return gaps
        
        for topic in topics["topics"]:
            topic_id = topic["topic_id"]
            top_words = topic.get("top_words", [])
            
            # Compute mission relevance
            relevance_score = self._compute_mission_relevance(top_words)
            
            # Compute paper density (inverse of gap)
            paper_count = len([w for w in top_words if w in str(paper_texts)])
            density = min(100, paper_count * 10)
            
            # Gap score = high relevance + low density
            gap_score = (relevance_score * 100 - density) / 100
            
            if gap_score > 0.3:  # Threshold for significant gap
                gaps.append({
                    "topic_id": topic_id,
                    "keywords": top_words[:10],
                    "mission_relevance": round(relevance_score, 2),
                    "paper_density": density,
                    "gap_score": round(gap_score, 2),
                    "recommended_experiments": self._suggest_experiments(top_words),
                    "nearest_topics": [],  # Placeholder
                })
        
        # Sort by gap score
        gaps.sort(key=lambda x: x["gap_score"], reverse=True)
        return gaps[:10]  # Top 10 gaps
    
    def _compute_mission_relevance(self, keywords: List[str]) -> float:
        """Compute how relevant keywords are to mission needs."""
        relevance = 0
        total_checks = 0
        
        keywords_lower = [k.lower() for k in keywords]
        
        for category, mission_words in self.mission_keywords.items():
            for mw in mission_words:
                total_checks += 1
                if any(mw in kw or kw in mw for kw in keywords_lower):
                    relevance += 1
        
        return relevance / max(total_checks, 1)
    
    def _suggest_experiments(self, keywords: List[str]) -> List[str]:
        """Suggest experiments based on keywords."""
        suggestions = []
        
        keywords_str = " ".join(keywords).lower()
        
        if "bone" in keywords_str or "muscle" in keywords_str:
            suggestions.append("Investigate countermeasures for musculoskeletal degradation")
        if "radiation" in keywords_str:
            suggestions.append("Test novel radiation shielding materials")
        if "plant" in keywords_str or "growth" in keywords_str:
            suggestions.append("Optimize plant growth protocols for space agriculture")
        if "stress" in keywords_str or "psychology" in keywords_str:
            suggestions.append("Develop crew psychological support interventions")
        
        if not suggestions:
            suggestions.append(f"Investigate {keywords[0] if keywords else 'topic'} under microgravity conditions")
        
        return suggestions[:3]

class MissionInsightGenerator:
    """Generate mission-relevant insights and recommendations."""
    
    def __init__(self):
        self.mission_keywords = MISSION_KEYWORDS
    
    def generate_insights(self, claims: Dict, paper_texts: Dict[str, str]) -> List[Dict]:
        """Generate mission insights from claims."""
        insights = []
        
        for norm_claim, data in claims.items():
            claim_text = data["claim"]
            
            # Categorize by mission area
            category = self._categorize_claim(claim_text)
            if not category:
                continue
            
            # Determine risk level
            risk_level = self._assess_risk(claim_text, data["consensus_score"])
            
            # Generate recommendation
            recommendation = self._generate_recommendation(claim_text, category)
            
            insights.append({
                "title": claim_text.title(),
                "category": category,
                "risk_level": risk_level,
                "confidence": data["consensus_score"],
                "confidence_badge": data["confidence_badge"],
                "finding": data["supporting_snippets"][0]["sentence"] if data["supporting_snippets"] else "",
                "recommendation": recommendation,
                "supporting_papers": data["supporting_papers"],
                "top_papers": [s["paper_id"] for s in data["supporting_snippets"][:3]],
            })
        
        # Sort by risk level and confidence
        risk_order = {"high": 3, "medium": 2, "low": 1}
        insights.sort(key=lambda x: (risk_order.get(x["risk_level"], 0), x["confidence"]), reverse=True)
        
        return insights[:20]  # Top 20 insights
    
    def _categorize_claim(self, claim: str) -> Optional[str]:
        """Categorize claim by mission area."""
        claim_lower = claim.lower()
        
        for category, keywords in self.mission_keywords.items():
            if any(kw in claim_lower for kw in keywords):
                return category.replace("_", " ").title()
        
        return None
    
    def _assess_risk(self, claim: str, confidence: float) -> str:
        """Assess risk level."""
        claim_lower = claim.lower()
        
        high_risk_keywords = ["damage", "loss", "degradation", "failure", "critical", "severe"]
        medium_risk_keywords = ["reduce", "decrease", "affect", "alter", "change"]
        
        if any(kw in claim_lower for kw in high_risk_keywords):
            return "high" if confidence > 50 else "medium"
        elif any(kw in claim_lower for kw in medium_risk_keywords):
            return "medium" if confidence > 50 else "low"
        else:
            return "low"
    
    def _generate_recommendation(self, claim: str, category: str) -> str:
        """Generate actionable recommendation."""
        claim_lower = claim.lower()
        
        if "radiation" in claim_lower:
            return "Consider enhanced radiation shielding or scheduling EVAs during solar minimum periods"
        elif "bone" in claim_lower or "muscle" in claim_lower:
            return "Implement resistance exercise protocols and nutritional countermeasures"
        elif "plant" in claim_lower:
            return "Optimize growth chamber parameters and investigate hardy cultivars"
        elif "stress" in claim_lower or "psychology" in claim_lower:
            return "Enhance crew selection protocols and provide real-time psychological support"
        else:
            return f"Investigate {category.lower()} implications and develop appropriate countermeasures"

def run_advanced_analysis(sample_n: Optional[int] = None):
    """Run complete advanced analysis pipeline."""
    logger.info("🔬 Starting advanced analysis...")
    
    # Load text files
    text_files = list(TEXT_DIR.glob("*_full.txt"))
    if sample_n:
        text_files = text_files[:sample_n]
    
    if not text_files:
        logger.warning("No text files found for analysis")
        return
    
    # Step 1: Extract claims
    logger.info("📋 Extracting claims from papers...")
    extractor = ClaimExtractor()
    all_claims = []
    
    paper_texts = {}
    for text_path in text_files:
        paper_id = text_path.stem.replace("paper_", "").replace("_full", "")
        
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            paper_texts[paper_id] = text
            
            # Extract from results section if available
            sections_path = text_path.parent / f"paper_{paper_id}_sections.json"
            if sections_path.exists():
                with open(sections_path, 'r', encoding='utf-8') as f:
                    sections = json.load(f)
                
                for section_name in ["results", "conclusion", "abstract"]:
                    if sections.get(section_name):
                        claims = extractor.extract_from_text(sections[section_name], paper_id, section_name)
                        all_claims.extend(claims)
            else:
                claims = extractor.extract_from_text(text[:5000], paper_id, "full")  # Use first 5000 chars
                all_claims.extend(claims)
        
        except Exception as e:
            logger.error(f"Error extracting claims from {paper_id}: {e}")
    
    logger.info(f"✅ Extracted {len(all_claims)} claims from {len(text_files)} papers")
    
    # Step 2: Compute consensus
    logger.info("🤝 Computing consensus scores...")
    analyzer = ConsensusAnalyzer()
    consensus_data = analyzer.compute_consensus(all_claims)
    
    # Save consensus data
    with open(CLAIMS_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            "total_claims": len(all_claims),
            "unique_claims": len(consensus_data),
            "claims": consensus_data
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Computed consensus for {len(consensus_data)} unique claims")
    
    # Step 3: Detect knowledge gaps
    logger.info("🔍 Detecting knowledge gaps...")
    gap_detector = KnowledgeGapDetector()
    
    # Load topics if available
    topics_path = ROOT / "topics" / "topics.json"
    topics = {}
    if topics_path.exists():
        with open(topics_path, 'r', encoding='utf-8') as f:
            topics = json.load(f)
    
    gaps = gap_detector.detect_gaps(topics, paper_texts)
    
    # Save gaps
    with open(GAPS_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            "total_gaps": len(gaps),
            "gaps": gaps
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Detected {len(gaps)} knowledge gaps")
    
    # Step 4: Generate mission insights
    logger.info("🚀 Generating mission insights...")
    insight_gen = MissionInsightGenerator()
    insights = insight_gen.generate_insights(consensus_data, paper_texts)
    
    # Save insights
    with open(MISSION_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            "total_insights": len(insights),
            "insights": insights
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Generated {len(insights)} mission insights")
    
    # Summary
    logger.info("\n📊 Advanced Analysis Complete!")
    logger.info(f"   - Claims extracted: {len(all_claims)}")
    logger.info(f"   - Consensus claims: {len(consensus_data)}")
    logger.info(f"   - Knowledge gaps: {len(gaps)}")
    logger.info(f"   - Mission insights: {len(insights)}")
    
    return {
        "claims": len(all_claims),
        "consensus": len(consensus_data),
        "gaps": len(gaps),
        "insights": len(insights)
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_advanced_analysis(sample_n=10)

