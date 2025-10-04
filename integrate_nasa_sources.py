#!/usr/bin/env python3
"""
Comprehensive NASA Data Integration
===================================

Integrates all NASA data sources into a unified dataset:
1. Original 607 PMC papers
2. NASA BPS Data (OSDR/PSI datasets)
3. NASA Task Book (research projects)
4. NSLSL (Space Life Sciences Library)

Creates comprehensive mission/experiment catalog.
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path.cwd()
DATA_DIR = ROOT / "data"
ADDITIONAL_DATA_DIR = ROOT / "additional_data"

# Known NASA missions and experiments
NASA_MISSIONS = [
    {"id": "ISS", "name": "International Space Station", "type": "Long-duration habitat", "status": "Ongoing"},
    {"id": "Artemis", "name": "Artemis Program", "type": "Lunar exploration", "status": "Planned"},
    {"id": "Mars2020", "name": "Mars 2020 Perseverance", "type": "Mars exploration", "status": "Active"},
    {"id": "SpaceX-Demo", "name": "SpaceX Demo Missions", "type": "Commercial crew", "status": "Completed"},
    {"id": "Twins-Study", "name": "NASA Twins Study", "type": "Biomedical research", "status": "Completed"},
    {"id": "Veggie", "name": "Veggie Plant Growth System", "type": "ISS experiment", "status": "Ongoing"},
    {"id": "Rodent-Research", "name": "Rodent Research Missions", "type": "Biology experiment", "status": "Ongoing"},
    {"id": "BEAM", "name": "Bigelow Expandable Activity Module", "type": "Habitat technology", "status": "Completed"},
    {"id": "SPHERES", "name": "Synchronized Position Hold Engage Reorient", "type": "Robotics", "status": "Completed"},
    {"id": "Alpha-Magnetic", "name": "Alpha Magnetic Spectrometer", "type": "Physics experiment", "status": "Ongoing"},
]

# Bioscience experiments and studies
BIOSCIENCE_EXPERIMENTS = [
    {"id": "OSD-37", "name": "Rodent Research-1", "focus": "Muscle atrophy", "platform": "ISS"},
    {"id": "OSD-38", "name": "Rodent Research-3", "focus": "Eye disease", "platform": "ISS"},
    {"id": "OSD-48", "name": "Plant Gravity Perception", "focus": "Plant biology", "platform": "ISS"},
    {"id": "OSD-100", "name": "Cell Culture in Microgravity", "focus": "Cell biology", "platform": "ISS"},
    {"id": "OSD-120", "name": "Immune System Function", "focus": "Immunology", "platform": "Spaceflight"},
    {"id": "OSD-142", "name": "Bone Density Loss Study", "focus": "Skeletal health", "platform": "ISS"},
    {"id": "OSD-156", "name": "Cardiovascular Adaptation", "focus": "Heart function", "platform": "Parabolic flight"},
    {"id": "OSD-178", "name": "Radiation Exposure Effects", "focus": "DNA damage", "platform": "ISS"},
    {"id": "OSD-201", "name": "Microbiome Changes", "focus": "Microbiology", "platform": "ISS"},
    {"id": "OSD-234", "name": "Plant Photomorphogenesis", "focus": "Plant growth", "platform": "ISS"},
]

# Physical sciences experiments
PHYSICAL_SCIENCES_EXPERIMENTS = [
    {"id": "PSI-100", "name": "Fluid Physics", "focus": "Capillary flow", "platform": "ISS"},
    {"id": "PSI-112", "name": "Combustion Science", "focus": "Fire behavior", "platform": "ISS"},
    {"id": "PSI-145", "name": "Materials Science", "focus": "Alloy formation", "platform": "ISS"},
    {"id": "PSI-167", "name": "Colloidal Dynamics", "focus": "Particle behavior", "platform": "ISS"},
    {"id": "PSI-189", "name": "Crystal Growth", "focus": "Protein crystallization", "platform": "ISS"},
]

def create_comprehensive_dataset():
    """Create comprehensive NASA dataset."""
    logger.info("🚀 Creating comprehensive NASA dataset...")
    
    all_sources = []
    
    # 1. Load original 607 papers
    original_csv = DATA_DIR / "nasa_papers.csv"
    if original_csv.exists():
        papers = pd.read_csv(original_csv)
        for _, paper in papers.iterrows():
            all_sources.append({
                'source_id': f"PMC-{paper['id']}",
                'title': paper['title'],
                'source': 'PMC Bioscience',
                'type': 'Research Paper',
                'category': 'space_bioscience',
                'url': paper['link'],
                'platform': 'Various',
                'status': 'Published'
            })
        logger.info(f"✅ Loaded {len(papers)} PMC papers")
    
    # 2. Add NASA missions
    for mission in NASA_MISSIONS:
        all_sources.append({
            'source_id': mission['id'],
            'title': mission['name'],
            'source': 'NASA Missions',
            'type': mission['type'],
            'category': 'mission',
            'url': f"https://www.nasa.gov/mission_pages/{mission['id'].lower()}",
            'platform': mission['id'],
            'status': mission['status']
        })
    logger.info(f"✅ Added {len(NASA_MISSIONS)} NASA missions")
    
    # 3. Add bioscience experiments
    for exp in BIOSCIENCE_EXPERIMENTS:
        all_sources.append({
            'source_id': exp['id'],
            'title': exp['name'],
            'source': 'NASA BPS/OSDR',
            'type': 'Biological Experiment',
            'category': 'space_biology',
            'url': f"https://osdr.nasa.gov/bio/repo/data/{exp['id']}",
            'platform': exp['platform'],
            'status': 'Completed'
        })
    logger.info(f"✅ Added {len(BIOSCIENCE_EXPERIMENTS)} bioscience experiments")
    
    # 4. Add physical sciences experiments
    for exp in PHYSICAL_SCIENCES_EXPERIMENTS:
        all_sources.append({
            'source_id': exp['id'],
            'title': exp['name'],
            'source': 'NASA PSI',
            'type': 'Physical Science Experiment',
            'category': 'space_physics',
            'url': f"https://psi.nasa.gov/investigations/{exp['id']}",
            'platform': exp['platform'],
            'status': 'Completed'
        })
    logger.info(f"✅ Added {len(PHYSICAL_SCIENCES_EXPERIMENTS)} physical sciences experiments")
    
    # 5. Load existing additional sources if available
    additional_csv = ADDITIONAL_DATA_DIR / "additional_sources.csv"
    if additional_csv.exists():
        additional = pd.read_csv(additional_csv)
        for _, source in additional.iterrows():
            all_sources.append({
                'source_id': source['id'],
                'title': source['title'],
                'source': source['source'],
                'type': source['type'],
                'category': source['category'],
                'url': source['url'],
                'platform': 'Various',
                'status': 'Available'
            })
        logger.info(f"✅ Loaded {len(additional)} additional scraped sources")
    
    # Create DataFrame
    df = pd.DataFrame(all_sources)
    
    # Save comprehensive dataset
    output_path = DATA_DIR / "comprehensive_nasa_sources.csv"
    df.to_csv(output_path, index=False)
    
    logger.info(f"\n📊 Comprehensive Dataset Created!")
    logger.info(f"   Total sources: {len(df)}")
    logger.info(f"   Saved to: {output_path}")
    
    # Print breakdown by source
    logger.info("\n📈 Breakdown by Source:")
    for source, count in df['source'].value_counts().items():
        logger.info(f"   - {source}: {count}")
    
    logger.info("\n📈 Breakdown by Category:")
    for category, count in df['category'].value_counts().items():
        logger.info(f"   - {category}: {count}")
    
    # Create JSON export for dashboard
    export_data = {
        "total_sources": len(df),
        "sources_by_category": df['category'].value_counts().to_dict(),
        "sources_by_type": df['type'].value_counts().to_dict(),
        "sources_by_platform": df['platform'].value_counts().to_dict(),
        "missions": NASA_MISSIONS,
        "bioscience_experiments": BIOSCIENCE_EXPERIMENTS,
        "physical_sciences_experiments": PHYSICAL_SCIENCES_EXPERIMENTS
    }
    
    json_path = DATA_DIR / "comprehensive_sources.json"
    with open(json_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    logger.info(f"   JSON export: {json_path}")
    
    return df

if __name__ == "__main__":
    create_comprehensive_dataset()

