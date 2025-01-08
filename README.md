# aws-hackathon-cost-optimization-tool

cost-optimization-tool/  
│  
├── lambda-functions/  
│       ├── bbi-hackathon-identifier.py    
│       ├── bbi-hackathon-pricecalc.py  
│       ├── bbi-hackathon-cleanup.py  
│  
├── ui/  
│   ├── (Add your UI files here)  
│  
├── dynamodb/  
│   ├── (Add DynamoDB schema details or utility scripts here)  
│  
├── quicksight/  
│   ├── (Add QuickSight integration details or sample reports here)  
│  
└── README.md  

# Cost Optimization Tool

This repository contains a set of Lambda functions and associated components for identifying, analyzing, and cleaning up idle AWS resources to optimize costs. The solution includes:

1. **AWS Lambda Functions**:
   - `bbi-hackathon-identifier.py`: Identifies idle resources like EC2 instances and stores data in DynamoDB.
   - `bbi-hackathon-pricecalc.py`: Fetches the cost of idle resources using AWS Pricing API and provides insights for optimization.
   - `bbi-hackathon-cleanup.py`: Performs resource cleanup (e.g., terminating EC2 instances or archiving S3 objects) based on user approval.

2. **UI**: Built using Vercel, the interface allows users to approve or reject cleanup actions.
3. **DynamoDB**: Data storage for resource status, actions, and metadata.
4. **QuickSight Integration**: For interactive cost analysis and visualization.

---

## Features

- **Automated Identification**:
  - Monitors EC2 CPU utilization to determine idle instances.
  - Fetches pricing details for accurate cost estimation.

- **User-Driven Cleanup**:
  - UI for resource approval/rejection.
  - Cleanup includes terminating EC2 instances and archiving S3 objects to Deep Archive.

- **Real-Time Insights**:
  - Backup data from DynamoDB to Amazon QuickSight for cost-optimization dashboards.

---

## Requirements

### Prerequisites
- AWS Account with permissions for EC2, DynamoDB, S3, CloudWatch, and Lambda.
- Python 3.8 or later.
- AWS CLI configured for the appropriate region.

### Tools Used
- **AWS Lambda** for serverless execution.
- **DynamoDB** for data persistence.
- **Vercel** for front-end UI hosting.
- **Amazon QuickSight** for visualization and reporting.

---

## Setup Instructions

### 1. Clone Repository
git clone https://github.com/<your-github-username>/cost-optimization-tool.git
cd cost-optimization-tool

### 2. Deploy Lambda Functions
Navigate to the lambda-functions/ directory.

Zip each Lambda function script:
zip identify_idle_resources.zip identify_idle_resources.py
Upload the zip files to their respective Lambda functions in AWS.

### 3. Configure DynamoDB
Create a DynamoDB table named BBI_Resource_Optimization with the following schema:
Partition Key: resource-id (String)
Attributes: status, user-action, unused-time, cost-optimized, type-of-resource.

### 4. UI Deployment
Place your Vercel project files in the ui/ directory.
Follow Vercel's deployment guide to deploy the UI.

### 5. QuickSight Integration
Use the data from DynamoDB as a dataset.
Create a dashboard in Amazon QuickSight to visualize cost-saving opportunities.

---

## Lambda Functions Overview
###  Identify Idle Resources
File: identify_idle_resources.py
Description: Identifies idle EC2 instances based on low CPU utilization (< 50%) over a 5-minute window and stores the details in DynamoDB.

### Put Price of Idle Resources
File: put_price_of_idle_resources.py
Description: Fetches pricing details for running instances using AWS Pricing API and provides estimated costs for optimization.

### Cleanup Resources
File: cleanup_resources.py
Description: Cleans up resources (e.g., terminates EC2 instances, moves S3 objects to Deep Archive) based on UI approvals stored in DynamoDB.


