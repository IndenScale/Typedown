# 供应商 A - 响应证据映射


## 1. 形式与资格响应

```entity BidResponseItem: RESP-SUP-A-PHY-01
supplier_id: "SUP-A"
review_item_id: "REQ-PHY-01"
response_text: "（现场实物检查，此处无电子证据）"
```

```entity BidResponseItem: RESP-SUP-A-QUAL-02
supplier_id: "SUP-A"
review_item_id: "REQ-QUAL-02"
evidences:
  - id: "CERT-ISO9001" # 引用已提取的证书实体
    name: "ISO9001 Certificate"
    evidence_source:
      location:
        file_name: "资格证明文件.pdf"
        page_start: 12
        snippet_content: "有效期至 2026年..."
```

## 2. 详细评分响应

### [SCORE-TECH-01] 架构设计

```entity BidResponseItem: RESP-SUP-A-TECH-01
supplier_id: "SUP-A"
review_item_id: "SCORE-TECH-01"
evidences:
  - location:
      file_name: "技术方案.pdf"
      page_start: 45
      page_end: 52
      snippet_content: "本方案采用异地双活数据中心架构，RPO=0..."
```

### [SCORE-BIZ-01] 业绩证明

```entity BidResponseItem: RESP-SUP-A-BIZ-01
supplier_id: "SUP-A"
review_item_id: "SCORE-BIZ-01"
evidences:
  - location:
      file_name: "业绩合同集.pdf"
      page_start: 1
      snippet_content: "合同金额：1200万元"
  - location:
      file_name: "业绩合同集.pdf"
      page_start: 15
      snippet_content: "合同金额：1500万元"
```
