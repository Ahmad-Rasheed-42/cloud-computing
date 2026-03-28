Architectural Design Report: UniEvent Platform

Course: CE 308/408 Cloud Computing Project: Deployment of a Scalable University Event Management System on AWS Role: Cloud Architect 

Executive Summary
This report outlines the architectural design and deployment strategy for UniEvent, a cloud-hosted web application centralized for student activity registration and event discovery. To eliminate manual data entry, the system automatically aggregates data from an external Open API. The infrastructure is designed natively on Amazon Web Services (AWS) using VPC, EC2, S3, IAM, and Elastic Load Balancing to ensure a secure, scalable, and fault-tolerant environment capable of handling peak registration loads.

1. External Data Integration (Open API)
To treat external events as official university events, the Ticketmaster Discovery API was selected and integrated.


Justification: Ticketmaster is a highly reliable public listing service that provides structured JSON data. It fulfills all data requirements by consistently delivering event titles, dates, venues, descriptions, and high-resolution promotional images.


Application Logic: A backend Python script utilizes the requests library to periodically fetch event data. The data is parsed, formatted, and prepared for display on the frontend as "University Events".

2. Storage Architecture (Amazon S3)
Amazon S3 is utilized to decouple storage from compute resources, keeping the application servers stateless.


Media Storage: As event data is fetched, the Python script extracts image URLs and utilizes the boto3 SDK to securely upload event posters directly to an S3 bucket.


Data Persistence: The processed JSON event data is stored persistently in S3.

Delivery: S3 Bucket Policies and Cross-Origin Resource Sharing (CORS) rules are configured to allow the HTML/JavaScript frontend to dynamically read and render the university_events.json file directly to the users.

3. Network Design (Amazon VPC)
The foundation of the architecture is a custom Virtual Private Cloud (VPC) designed for high availability and strict security.

Availability Zones (AZs): The network spans two independent Availability Zones to prevent a single point of failure.

Subnet Strategy: The VPC is divided into Public and Private subnets. The web application runs on multiple EC2 instances deployed exclusively inside the private subnets, shielding them from direct internet access.

NAT Gateway: A NAT Gateway is deployed in the public subnet, allowing the private EC2 instances to securely route outbound traffic to fetch data from the Ticketmaster API without exposing the servers to inbound internet traffic.

4. Compute and Scalability (EC2 & ELB)
The compute layer is designed to dynamically adapt to varying traffic loads, such as society recruitment drives.

Elastic Load Balancing (ELB): An Application Load Balancer is placed in the public subnets to serve as the single point of entry. It distributes incoming user traffic evenly across the backend instances.

Auto Scaling Group (ASG): The EC2 instances are managed by an ASG with a minimum capacity of two instances. If an instance becomes unhealthy or fails, the ASG automatically terminates it and provisions a replacement, guaranteeing continuous system operation.

5. Security and Access Management (IAM & Security Groups)
Security awareness is embedded at both the network and identity levels.


Identity and Access Management (IAM): Following the principle of least privilege, an IAM Role with specific S3 access policies is attached to the EC2 instances. This allows the backend application to interact with S3 without utilizing hardcoded AWS credentials.

Security Groups: * The ALB Security Group permits inbound HTTP/HTTPS traffic from the public internet.

The EC2 Security Group strictly limits inbound access, only accepting traffic that originates from the Load Balancer, effectively neutralizing direct access attacks.
