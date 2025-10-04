#!/usr/bin/env python3
"""
Create sample PDF files for testing the NASA Bioscience Summarizer pipeline.
"""

import os
from pathlib import Path

# Create sample PDF content
sample_papers = [
    {
        "id": 1,
        "title": "Mice in Bion-M 1 space mission: training and selection",
        "content": """
        Abstract
        The Bion-M1 mission provided a unique opportunity to study the effects of spaceflight on mammalian physiology. 
        This study examined the training and selection process for mice participating in the 30-day orbital mission. 
        Mice were selected based on health criteria, behavioral assessments, and stress tolerance. Training protocols 
        included habituation to confinement and simulated microgravity conditions.
        
        Introduction
        Spaceflight presents numerous challenges to mammalian physiology, including microgravity, radiation exposure, 
        and psychological stress. Understanding these effects is crucial for long-duration space missions. The Bion-M1 
        mission provided an opportunity to study these effects in a controlled environment.
        
        Methods
        Twenty mice were selected from a pool of 50 candidates based on health screenings, behavioral tests, and 
        stress response assessments. Selected mice underwent 30 days of training including confinement habituation, 
        vibration exposure, and simulated microgravity conditions using a rotating platform.
        
        Results
        The training protocol significantly improved mouse adaptation to spaceflight conditions. Mice showed reduced 
        stress responses and improved behavioral adaptation. Post-flight analysis revealed changes in bone density, 
        muscle mass, and immune function consistent with microgravity effects.
        
        Conclusion
        The training and selection protocol successfully prepared mice for spaceflight conditions. These findings 
        provide valuable insights for future space biology experiments and have implications for human spaceflight 
        preparation.
        """
    },
    {
        "id": 2,
        "title": "Microgravity induces pelvic bone loss through osteoclastic activity",
        "content": """
        Abstract
        Microgravity exposure leads to significant bone loss in astronauts, particularly in weight-bearing bones. 
        This study investigated the cellular mechanisms underlying pelvic bone loss in a murine model of spaceflight. 
        We found that microgravity increases osteoclastic activity while inhibiting osteoblastic function, leading 
        to net bone resorption.
        
        Introduction
        Bone loss is one of the most significant health concerns for astronauts during long-duration spaceflight. 
        Understanding the cellular mechanisms is essential for developing effective countermeasures. This study 
        focused on the pelvic region, which experiences significant bone loss in microgravity.
        
        Methods
        Thirty-six mice were subjected to hindlimb unloading to simulate microgravity conditions. Bone density 
        measurements were taken at baseline and after 14 days of unloading. Osteoclast and osteoblast activity 
        were assessed through histological analysis and gene expression studies.
        
        Results
        Hindlimb unloading resulted in significant pelvic bone loss (15% reduction in bone mineral density). 
        Osteoclast activity increased by 40%, while osteoblast activity decreased by 25%. Gene expression 
        analysis revealed upregulation of osteoclastogenic factors and downregulation of osteoblastic markers.
        
        Conclusion
        Microgravity-induced pelvic bone loss is primarily mediated by increased osteoclastic activity and 
        decreased osteoblastic function. These findings suggest that targeting osteoclast activity may be 
        an effective strategy for preventing bone loss in spaceflight.
        """
    },
    {
        "id": 3,
        "title": "Stem Cell Health and Tissue Regeneration in Microgravity",
        "content": """
        Abstract
        Stem cell function is crucial for tissue regeneration and maintenance. This study examined how microgravity 
        affects stem cell health and regenerative capacity using human mesenchymal stem cells cultured in simulated 
        microgravity conditions. We found that microgravity alters stem cell morphology, proliferation, and 
        differentiation potential.
        
        Introduction
        Stem cells play a vital role in tissue regeneration and repair. Understanding how spaceflight affects 
        stem cell function is important for maintaining astronaut health during long-duration missions. This 
        study investigated the effects of simulated microgravity on human mesenchymal stem cells.
        
        Methods
        Human mesenchymal stem cells were cultured in a rotating wall vessel to simulate microgravity conditions. 
        Cell morphology, proliferation rates, and differentiation potential were assessed over 7 days. Gene 
        expression analysis was performed to identify molecular changes associated with microgravity exposure.
        
        Results
        Simulated microgravity altered stem cell morphology, with cells becoming more rounded and less adherent. 
        Proliferation rates decreased by 30%, and differentiation potential was significantly impaired. Gene 
        expression analysis revealed changes in cytoskeletal genes, growth factor receptors, and differentiation markers.
        
        Conclusion
        Microgravity significantly impairs stem cell function and regenerative capacity. These findings have 
        important implications for astronaut health and suggest the need for countermeasures to maintain 
        stem cell function during spaceflight.
        """
    }
]

def create_sample_pdfs():
    """Create sample PDF files for testing."""
    papers_dir = Path("papers")
    papers_dir.mkdir(exist_ok=True)
    
    for paper in sample_papers:
        # Create a simple text file that can be processed as if it were a PDF
        pdf_path = papers_dir / f"paper_{paper['id']}.pdf"
        
        # For testing purposes, we'll create a text file with the content
        # In a real scenario, this would be a proper PDF
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write(paper['content'])
        
        print(f"Created sample paper {paper['id']}: {paper['title']}")
    
    print(f"\nCreated {len(sample_papers)} sample papers in {papers_dir}")

if __name__ == "__main__":
    create_sample_pdfs()
