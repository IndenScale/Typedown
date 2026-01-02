```config:python
import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from datetime import date

# Export Common Models
from use_cases.bid_agent.models.core import BidProject, ProjectDomain, FileResource, DocumentType
from use_cases.bid_agent.models.review import ScoringItem, ScoringType, BidResponseItem, ReviewResultEntry, Criticality
from use_cases.bid_agent.models.evidence import Certificate, Achievement, EvidenceSource, DocLocation, ValidationStatus, Person
from use_cases.bid_agent.models.verification import FactCheckRecord
```
