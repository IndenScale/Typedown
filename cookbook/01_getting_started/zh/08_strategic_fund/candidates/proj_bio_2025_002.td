# 候选项目：第三代微藻生物燃料 (Algae Biofuel Gen-3)

探索利用合成生物学技术改造微藻，以实现高效率的碳捕获与燃油合成。

## 1. 科学愿景 (Scientific Vision)

随着全球碳中和目标的逼近，寻找可持续的液体燃料替代品变得至关重要。传统的玉米乙醇或废油柴油存在"与人争粮"或原料来源不稳的问题。微藻（Microalgae）光合作用效率高，且可利用盐碱地如果不适宜耕作的土地，是理想的生物工厂。本项目旨在通过 CRISPR-Cas9 基因编辑技术，敲除微藻的脂质分解代谢通路，并过表达脂肪酸合成酶，从而将细胞含油量提升至 60% 以上。

## 2. 详细实施方案 (Detailed Implementation)

### 2.1 菌种筛选与改造 (Strain Engineering)
我们将以 *Chlamydomonas reinhardtii*（莱茵衣藻）和 *Nannochloropsis oceanica*（微拟球藻）为底盘细胞。
*   **靶点 1**: 敲除 ADP-glucose pyrophosphorylase (AGPase)，阻断淀粉合成，迫使碳流向脂质。
*   **靶点 2**: 引入外源的高效 RuBisCO 酶，提高固碳效率。

### 2.2 规模化培养工艺 (Cultivation Process)
采用创新的"跑道池"（Raceway Pond）与光生物反应器（PBR）耦合系统。
*   **阶段 I**: 在 PBR 中进行高密度接种培养，控制无菌环境。
*   **阶段 II**: 转移至室外跑道池，利用廉价阳光和工业废气（CO2源）进行积累培养。

### 2.3 下游提炼 (Downstream Processing)
开发基于离子液体的湿法萃取技术，避免干燥过程的高能耗，实现细胞破壁与油脂分离的一步完成。

## 3. 申报实体 (Structured Entity)

```entity ProjectApplication: proj_bio_2025_002
title: "Algae Biofuel Gen-3 Research"
applicant_id: "Li Qiang"
domain: "Biotechnology"
requested_budget_cny: 8000000.0
status: "Draft"
plan:
  abstract: "Engineering microalgae for high lipid production using CRISPR."
  background: "Need for sustainable liquid fuels without competing for arable land."
  objectives: 
    - "Achieve 60% lipid content in dry weight."
    - "Reduce CO2 capture cost to < $50/ton."
  methodology_steps: 
    - "Genetic Modification (CRISPR)"
    - "Laboratory Screening"
    - "Pilot Scale Cultivation"
    - "Extraction Optimization"
  technical_challenges: 
    - "Genetic Stability of Modified Strains"
    - "Contamination in Open Ponds"
    - "Energy Balance of Extraction"
  milestones:
    - date: "2025-04-01"
      goal: "Strain Created"
      deliverables: ["5 Mutant Strains", "Genomic Sequencing Data"]
    - date: "2025-09-01"
      goal: "Lab Scale Validation"
      deliverables: ["Growth Curve Report", "Lipid Analysis"]
    - date: "2026-03-01"
      goal: "Pilot Reactor Run"
      deliverables: ["100L Bio-oil Sample", "Techno-Economic Assessment"]
  budget_breakdown:
    - category: "Equipment"
      amount: 3000000.0
      justification: "Photobioreactors & Analytic Instruments"
    - category: "Personnel"
      amount: 3500000.0
      justification: "Biotechnologists & Lab Technicians"
    - category: "Outsourcing"
      amount: 500000.0
      justification: "Genome Sequencing Services"
    - category: "Travel"
      amount: 200000.0
      justification: "Field Trips to Algae Farms" 
  team_members: ["Li Qiang", "Intern Wang", "Dr. Green"]
```

## 4. 伦理与安全声明
本实验涉及转基因生物（GMO），我们将严格遵守国家生物安全法规，所有室外实验将在物理隔离的设施中进行，防止藻种逃逸造成生态污染。
