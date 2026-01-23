# Deploying a Full-Stack Task Management Application to AWS: A Complete Journey from Code to Cloud

## Introduction

Building an application is one thing. Deploying it to production in a way that is scalable, secure, and cost-effective is an entirely different challenge. Over the past three weeks, I embarked on a journey to take a full-stack task management application and deploy it to Amazon Web Services (AWS), transforming it from a local Docker setup into a production-ready cloud application.

This is the story of that journey, including every decision made, every challenge faced, and every lesson learned along the way.

## The Starting Point

The application itself was straightforward but complete. A task management system built with:

**Backend:** Flask (Python) providing a RESTful API with JWT authentication, PostgreSQL database integration, and comprehensive error handling.

**Frontend:** Next.js 14 (React with TypeScript) featuring a modern drag-and-drop interface built with TailwindCSS, real-time state management using Zustand, and server-side rendering capabilities.

**Database:** PostgreSQL with a normalized schema handling users, projects, and tasks with proper foreign key relationships.

Everything worked perfectly in Docker Compose on my local machine. The backend ran on port 5000, the frontend on port 3000, and PostgreSQL on port 5432. One command would spin up the entire stack. But local development and production deployment are vastly different beasts.

## The Goal

I wanted to deploy this application to AWS using best practices for production systems. This meant:

- High availability across multiple availability zones
- Secure network architecture with public and private subnets
- Auto-scaling to handle variable traffic loads
- Zero-downtime deployments through CI/CD automation
- Cost optimization to keep monthly expenses reasonable
- Production-grade monitoring and logging

The plan was to complete this in 12 phases over 3-4 weeks, documenting everything meticulously so others could follow the same path.

## Phase 1-2: Foundation and Networking

Every solid building needs a good foundation. In AWS, that foundation is the Virtual Private Cloud (VPC).

I created a VPC with a CIDR block of 10.0.0.0/16, giving us 65,536 possible IP addresses. Inside this VPC, I set up four subnets across two availability zones for high availability:

Two public subnets (10.0.1.0/24 and 10.0.2.0/24) where internet-facing resources like load balancers would live. Two private subnets (10.0.10.0/24 and 10.0.11.0/24) where the application containers and database would reside, protected from direct internet access.

An Internet Gateway provided the VPC's connection to the outside world. For the private subnets, a NAT Gateway in the first public subnet allowed outbound internet access without exposing the resources to inbound traffic. This is crucial for pulling Docker images from Amazon ECR and downloading system updates.

The security model was built on security groups acting as virtual firewalls. The load balancer security group allowed HTTP (port 80) and HTTPS (port 443) from anywhere. The ECS security group only accepted traffic from the load balancer on ports 3000 and 5000. The database security group only allowed PostgreSQL connections (port 5432) from the ECS tasks. Each layer could only communicate with exactly what it needed.

## Phase 3: Database Layer

For the database, I chose Amazon RDS with PostgreSQL 16.4. The decision to use a managed database service instead of running PostgreSQL in a container was deliberate. RDS handles backups, patching, replication, and failure recovery automatically.

I selected the db.t3.micro instance type, which provides 2 vCPUs and 1 GB of memory. For a learning project with minimal traffic, this was more than sufficient and cost-effective at around $15 per month. The database was configured with:

20 GB of SSD storage with auto-scaling enabled up to 100 GB. This means the database can grow automatically as data accumulates without manual intervention.

Multi-AZ deployment for high availability. Amazon maintains a synchronous standby replica in a different availability zone. If the primary fails, RDS automatically fails over to the standby, typically within 60-120 seconds.

Automated backups with a 7-day retention period, running daily at 3 AM EST. This provides point-in-time recovery capabilities.

Encryption at rest using AWS Key Management Service (KMS), ensuring data security even if storage media is compromised.

The database was placed in a private subnet and secured so only ECS tasks could connect. The master password was generated using a cryptographically secure random string.

## Phase 4: Container Registry

Docker images needed a home in AWS. Amazon Elastic Container Registry (ECR) serves this purpose. I created two private repositories: taskapp-backend and taskapp-frontend.

The process of getting images into ECR involved authenticating Docker to ECR, building the images locally, tagging them appropriately, and pushing them. For the backend, the Docker image included all Python dependencies, the Flask application code, and environment variable configuration. The frontend image, built using Next.js standalone mode, was particularly lightweight at around 150 MB compared to the typical 300+ MB of a standard Next.js production build.

ECR provides automatic image scanning for vulnerabilities and integrates seamlessly with ECS for deployments. Later in the project, I would configure lifecycle policies to automatically delete old images, keeping only the last 10 versions to control storage costs.

## Phase 5-6: Application Deployment with ECS Fargate

This is where things got interesting. Amazon Elastic Container Service (ECS) with Fargate launch type meant I could run containers without managing any EC2 instances. Fargate is truly serverless compute for containers.

I created an ECS cluster named taskapp-cluster. Within this cluster, I would run two services: one for the backend and one for the frontend.

**Backend Service Configuration:**

The task definition specified the container image from ECR, allocated 0.25 vCPU and 512 MB of memory (the smallest Fargate size), and configured seven environment variables including DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, and CORS_ORIGINS.

CloudWatch Logs were configured with a 30-day retention period to capture application logs. The service was set to run two tasks for high availability, placed in private subnets across both availability zones.

The Application Load Balancer (ALB) sat in the public subnets, receiving traffic from the internet and distributing it to the backend tasks. A target group with health checks on the /api/health endpoint ensured traffic only went to healthy containers.

**Frontend Service Configuration:**

The frontend presented unique challenges. Next.js applications use environment variables prefixed with NEXT_PUBLIC_ to expose values to the browser. However, these are compiled into the JavaScript bundle at build time, not read at runtime.

This meant I could not simply pass NEXT_PUBLIC_API_URL as an environment variable when starting the container. The API URL had to be baked into the image during the Docker build process using the --build-arg flag. This was a critical lesson: the frontend had to know the backend's URL before deployment, which meant building separate images for different environments.

The solution involved building the frontend image with the ALB's DNS name as the API URL, pushing it to ECR, and then deploying it to ECS. The frontend service also ran two tasks in private subnets.

**Path-Based Routing:**

The ALB used path-based routing to serve both services through a single endpoint. Requests to /api/* were routed to the backend target group with priority 1. All other requests (/*) went to the frontend target group as the default rule. This meant users could access everything through one domain without CORS complications.

## Phase 7: Custom Domain and SSL

Running the application on an ALB's auto-generated DNS name was functional but not professional. I already owned techveesolutions.com with a wildcard SSL certificate in AWS Certificate Manager.

Setting up the custom domain involved creating an A record in Route 53 pointing app.techveesolutions.com to the ALB using an alias record. Adding an HTTPS listener on port 443 to the ALB and attaching the existing SSL certificate enabled encrypted traffic.

The HTTP listener was configured to redirect all traffic to HTTPS with a 301 permanent redirect, ensuring users always connected securely.

However, this introduced a new problem: the frontend was still trying to call the backend using the old ALB DNS name. I had to rebuild the frontend Docker image with NEXT_PUBLIC_API_URL set to https://app.techveesolutions.com/api, push it to ECR, and redeploy. The backend's CORS_ORIGINS environment variable also needed updating to allow requests from the new domain.

After these changes, the application was live at https://app.techveesolutions.com with a valid SSL certificate and professional URL.

## Phase 8: Monitoring and Observability

You cannot manage what you cannot measure. CloudWatch became the central nervous system for monitoring the application.

I set up six critical alarms:

**Backend High CPU**: Triggers when backend tasks exceed 80% CPU utilization for 2 consecutive periods. This indicates the service is under heavy load and may need scaling.

**Backend Memory**: Alerts when memory usage exceeds 80%, which could indicate memory leaks or insufficient resources.

**Frontend High CPU**: Similar to backend CPU monitoring.

**Database CPU**: Monitors RDS CPU utilization, as database bottlenecks can impact the entire application.

**Database Connections**: Tracks active database connections against the maximum allowed. Running out of connections causes application failures.

**ALB Unhealthy Targets**: Immediately alerts if any target in the load balancer's target groups becomes unhealthy.

A CloudWatch dashboard provided visual monitoring with graphs showing CPU utilization, memory usage, active tasks, request counts, and database performance metrics all in one place.

Logs from both services were centralized in CloudWatch Logs with 30-day retention, providing the ability to search and analyze application behavior. Log Insights queries could quickly find errors, slow requests, or suspicious patterns.

## Phase 9: The Infrastructure as Code Attempt

At this point, I had a fully functional production deployment, but everything was created manually through the AWS CLI. This was not sustainable or repeatable.

I spent time exploring Terraform as a way to codify the infrastructure. The goal was to have all resources defined in version-controlled configuration files that could recreate the entire stack with a single command.

I created Terraform modules for the VPC, ECS cluster, RDS instance, ALB, and security groups. The state file was configured to be stored in an S3 bucket for team collaboration and state locking via DynamoDB to prevent concurrent modifications.

While the Terraform configuration worked and could deploy a parallel environment, I ultimately decided not to migrate the production infrastructure to Terraform. The manual AWS CLI approach had given me deeper understanding of each resource and their interdependencies. For this learning project, that hands-on knowledge was more valuable than the automation benefits Terraform provides.

However, the Terraform code remained in the repository as documentation of how the infrastructure could be defined as code for future projects.

## Phase 10: CI/CD Automation

Manual deployments had to go. Every code change required building Docker images locally, pushing to ECR, creating new task definitions, and updating ECS services. This was time-consuming and error-prone.

GitHub Actions provided the automation layer. I created two workflow files that would handle deployments automatically.

**IAM Configuration:**

First, I created an IAM user named github-actions-ecs-deployer with a custom policy granting exactly the permissions needed: ECR read/write, ECS service and task definition management, IAM PassRole for the task execution role, and CloudWatch Logs read access. This followed the principle of least privilege.

**GitHub Secrets:**

Eleven secrets were configured in the repository: AWS credentials (access key ID and secret access key), region, ECR repository names, ECS cluster and service names, and application secrets (DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY).

**Backend Workflow:**

Triggered on any push to the Cloud-Deployment branch that changed files in the backend/ directory. The workflow authenticated with AWS, built the Docker image, pushed it to ECR with both a commit SHA tag and the latest tag, downloaded the current task definition, and here is where it got tricky.

AWS returns task definitions with fields that it does not accept for registration, like taskDefinitionArn, revision, status, and several others. Trying to register a task definition with these fields present caused errors. The solution was using jq to filter out these incompatible fields before registration.

Additionally, the task definition's environment variables needed updating with the latest values from GitHub Secrets. The workflow used jq to completely replace the environment array with current values, ensuring secrets could be rotated without modifying the workflow.

After registering the new task definition, the workflow updated the ECS service, which triggered a rolling deployment. ECS gradually replaced old tasks with new ones, maintaining the desired task count throughout. Zero downtime.

**Frontend Workflow:**

Similar to the backend but with the critical addition of using --build-arg during the Docker build to bake the API URL into the image. The workflow also needed to update only two environment variables (NODE_ENV and NEXT_PUBLIC_API_URL) rather than the backend's seven.

**The Debugging Journey:**

Getting these workflows working required seven backend deployments and four frontend deployments. The main issues were:

Task definition incompatibility errors solved by stripping extra fields. Environment variables not updating because the amazon-ecs-render-task-definition GitHub Action could not handle environment updates, requiring a custom jq solution. Database authentication failures because the DATABASE_URL secret had the wrong password and was missing the SSL mode parameter.

Once solved, deployments became magical. Push code to GitHub, wait five minutes, and the changes were live in production with zero downtime.

## Phase 11: Cost Optimization and Auto-Scaling

With everything working, it was time to optimize costs. The infrastructure was running about $105 per month:

NAT Gateway: $33 (35% of total cost)
Application Load Balancer: $16.20
RDS db.t3.micro: $15.30
Backend ECS (2 tasks): $18
Frontend ECS (2 tasks): $9.75
CloudWatch and other services: $12

Running two tasks per service 24/7 was wasteful for a learning project with minimal traffic. Auto-scaling could reduce costs while maintaining the ability to handle load spikes.

**ECS Auto-Scaling Configuration:**

I registered both services as scalable targets with a minimum of 1 task and maximum of 4 tasks. Target tracking scaling policies were created using CPU utilization as the metric, with a target of 70%.

When CPU exceeds 70%, ECS scales out by adding tasks, waiting 60 seconds before allowing another scale-out (the cooldown period prevents rapid oscillations). When CPU drops below 63% (70% minus the 10% default deviation), ECS scales in by removing tasks after a 300-second cooldown.

The immediate impact was visible. As soon as auto-scaling was enabled, the services scaled from 2 tasks down to 1 task each because CPU usage was around 20-30%. This represented immediate cost savings of approximately $14 per month.

**Scheduled Scaling:**

Auto-scaling is reactive, but I also wanted proactive cost control. Scheduled scaling actions force specific capacity at certain times.

At 11 PM EST (4 AM UTC) Monday through Friday, a scheduled action sets both services to a minimum and maximum of 1 task. This prevents scaling during the night when traffic is zero.

At 6 AM EST (11 AM UTC) Monday through Friday, another scheduled action restores the minimum to 1 and maximum to 4, allowing auto-scaling during business hours.

Weekends remain at 1 task minimum throughout.

These cron expressions in UTC ensured predictable cost savings during known low-traffic periods.

**Budget Monitoring:**

I created a monthly budget of $100 with two notification thresholds. At 80% actual spending ($80), I receive an email alert. At 100% forecasted spending, another alert triggers. This provides early warning if costs trend higher than expected.

**Infrastructure Optimizations:**

RDS storage auto-scaling was enabled, allowing the database to grow from 20 GB to 100 GB as needed without manual intervention.

ECR lifecycle policies were configured to keep only the last 10 images per repository, automatically deleting older versions to control storage costs.

CloudWatch log retention was already set to 30 days from Phase 8, preventing unlimited log accumulation.

**Results:**

The monthly cost dropped to approximately $92, a 12% reduction. During low-traffic periods (nights and weekends), savings could reach 40% as tasks scale down to the minimum. The infrastructure now costs about $75-90 per month depending on actual usage patterns.

More importantly, the system can still handle traffic spikes. If CPU exceeds 70%, auto-scaling kicks in within 60 seconds, adding tasks up to the maximum of 4 per service (8 total tasks), providing 4x the capacity of the baseline.

## Technical Architecture Deep Dive

At this point, the architecture looked like this:

**External Layer:**

Users access https://app.techveesolutions.com through Route 53, which resolves to the Application Load Balancer in two public subnets across different availability zones.

**Load Balancing Layer:**

The ALB terminates SSL/TLS connections using the certificate from AWS Certificate Manager. It inspects the request path and routes /api/* requests to the backend target group, and all other requests to the frontend target group. Health checks run every 30 seconds, requiring two consecutive successes before considering a target healthy.

**Application Layer:**

Backend and frontend services run as ECS Fargate tasks in private subnets. Each task pulls its container image from ECR during startup, retrieves environment variables from the task definition, and begins accepting traffic through the load balancer.

Auto-scaling monitors CPU utilization via CloudWatch metrics, adjusting the number of running tasks between 1 and 4 based on demand.

**Database Layer:**

RDS PostgreSQL runs in private subnets across two availability zones in Multi-AZ configuration. Only ECS tasks can connect, enforced by security group rules. Automated backups run daily, and encryption protects data at rest.

**Monitoring Layer:**

All components send metrics to CloudWatch. ECS tasks stream logs to CloudWatch Logs. CloudWatch Alarms monitor critical metrics and send notifications via SNS. A CloudWatch Dashboard provides real-time visibility.

**Deployment Pipeline:**

Developers push code to GitHub. GitHub Actions workflows trigger on changes, building Docker images and pushing to ECR. The workflow registers new task definitions with ECS and updates services, triggering rolling deployments. Old tasks remain running until new tasks pass health checks, ensuring zero downtime.

## Challenges and Solutions

**Challenge: Next.js Environment Variables**

Problem: The frontend kept using localhost:5000 instead of the production API URL.

Root Cause: NEXT_PUBLIC_ environment variables are compiled into JavaScript bundles at build time, not read at runtime.

Solution: Use docker build --build-arg NEXT_PUBLIC_API_URL=... to bake the URL into the image during the build process. This required rebuilding and redeploying the frontend whenever the API URL changed.

**Challenge: Database Authentication in Production**

Problem: Backend tasks could not connect to RDS, showing password authentication failed errors.

Root Cause: The DATABASE_URL secret in GitHub had a placeholder password instead of the actual RDS master password, and was missing the sslmode=require parameter that RDS requires.

Solution: Update the GitHub secret with the correct connection string including the actual password and SSL mode. Redeploy the backend with the corrected secret.

**Challenge: Task Definition Incompatibility**

Problem: GitHub Actions workflow failed when trying to register task definitions with Unexpected key 'enableFaultInjection' found in params.

Root Cause: AWS ECS describe-task-definition returns fields that are not valid for register-task-definition, including enableFaultInjection, taskDefinitionArn, revision, status, and others.

Solution: Use jq to filter out incompatible fields before registering: jq 'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy, .enableFaultInjection)'

**Challenge: Environment Variables Not Updating**

Problem: Changes to GitHub Secrets were not reflected in deployed containers even after workflow ran successfully.

Root Cause: The amazon-ecs-render-task-definition GitHub Action only updates the container image, not environment variables.

Solution: Stop using the action for environment management. Instead, use jq to directly replace the entire environment array with current values from secrets, ensuring every deployment uses the latest configuration.

**Challenge: Git Bash Path Conversion**

Problem: AWS CLI commands with paths like /ecs/taskapp were converted to Windows paths like C:/Program Files/Git/ecs/taskapp.

Root Cause: Git Bash on Windows automatically converts Unix-style paths to Windows paths.

Solution: Prefix commands with MSYS_NO_PATHCONV=1 to disable automatic path conversion, or quote paths appropriately.

## Cost Analysis

Let me break down the monthly costs in detail:

**Fixed Costs (Cannot be easily reduced):**

NAT Gateway: $32.40 for the gateway itself plus approximately $0.60 for 10 GB of data processing per month. This is the single largest cost driver at 35% of the total. VPC endpoints could reduce this but would add their own costs.

Application Load Balancer: $16.20 per month for a standard ALB. This includes the base hourly charge plus LCU (Load Balancer Capacity Unit) charges based on traffic. For this low-traffic application, LCU charges are minimal.

**Variable Costs (Optimized through auto-scaling):**

Backend ECS: Originally $18 for two tasks running 24/7. After auto-scaling, approximately $12 with an average of 1.3 tasks. Each task costs about $0.012 per hour (0.25 vCPU at $0.04048 per vCPU-hour, plus 0.5 GB at $0.004445 per GB-hour).

Frontend ECS: Originally $9.75 for two tasks. After auto-scaling, approximately $6.50 with 1.3 average tasks. Same per-task cost as backend.

**Database:**

RDS db.t3.micro: $15.30 per month in a Multi-AZ deployment. This includes the instance cost, storage cost for 20 GB of SSD (at $0.115 per GB-month), and backup storage within the free tier.

**Monitoring and Logs:**

CloudWatch: Approximately $8 per month including custom metrics, alarms (10 alarms at $0.10 each), and log ingestion/storage. With 30-day retention, about 2 GB of logs per month at $0.50 per GB ingestion.

**Storage and DNS:**

ECR: Approximately $0.50 per month for storing about 5 GB of container images (10 images at ~500 MB each). Lifecycle policies keep this from growing.

Route 53: $0.50 per month for the hosted zone, plus negligible query charges.

**Total:** Approximately $92 per month, or about $1,104 per year.

For comparison, running this same infrastructure without auto-scaling would cost around $105 per month. Reserved Instances could reduce costs further (saving approximately $10 per month with a 1-year commitment), but are not recommended for learning projects.

The biggest potential saving would come from eliminating the NAT Gateway, but this would break deployments as ECS tasks could not pull images from ECR. An alternative architecture using VPC endpoints for ECR would reduce NAT traffic but add endpoint costs of approximately $14 per month, resulting in minimal net savings.

## Lessons Learned

**Start with Infrastructure as Code:** While I learned immensely from manual AWS CLI commands, starting a production project with Terraform or CloudFormation would have saved time and ensured consistency. The manual approach was valuable for learning but not scalable.

**Environment-Specific Builds Matter:** Next.js environment variables taught me that some frameworks require build-time configuration. Understanding when values are baked in versus when they are read at runtime is critical.

**Security Groups Are Powerful:** The layered security model using security groups provided defense in depth. Even if one layer were compromised, the next layer would still protect resources.

**Monitoring Is Not Optional:** CloudWatch alarms caught issues before they became outages. The investment in proper monitoring paid for itself immediately.

**Auto-Scaling Saves Money:** The 12% immediate cost reduction from auto-scaling proved that right-sizing infrastructure matters. Over-provisioning "just in case" wastes money.

**Document Everything:** Writing detailed documentation for each phase created a knowledge base that made troubleshooting faster and helped me understand the entire system holistically.

**Secrets Management Requires Care:** The database password issue highlighted the importance of proper secrets management. AWS Secrets Manager with automatic rotation would be the next evolution.

**Test Disaster Recovery:** I configured backups and Multi-AZ deployment but never actually tested a disaster recovery scenario. This is a gap that should be addressed before calling the system truly production-ready.

## What I Would Do Differently

**Use Infrastructure as Code from Day One:** For a production project, I would start with Terraform or CloudFormation immediately. The learning value of manual commands does not outweigh the benefits of version-controlled, repeatable infrastructure.

**Implement Blue-Green Deployments:** While rolling deployments work well, blue-green deployments provide even safer releases with instant rollback capabilities.

**Add a Staging Environment:** Deploying directly to production is risky. A staging environment that mirrors production would catch issues before they affect users.

**Use AWS Secrets Manager:** Instead of storing secrets in GitHub, AWS Secrets Manager with automatic rotation would improve security and eliminate the manual password update problem.

**Implement Application-Level Metrics:** CloudWatch provides infrastructure metrics, but application-level metrics (request latency, error rates, business metrics) would provide better insights. Integration with something like Datadog or New Relic would be valuable.

**Add a CDN:** Serving the frontend through CloudFront instead of directly from ECS would improve global performance and reduce costs. The frontend assets could even be served from S3 behind CloudFront, eliminating the frontend ECS service entirely.

**Use Reserved Instances for Stable Resources:** For resources with predictable, steady usage like RDS and the NAT Gateway, Reserved Instances would reduce costs by 30-40% with a 1-year commitment.

## Performance and Reliability Observations

After running in production for several weeks, some interesting patterns emerged.

**Response Times:**

The application consistently responds in under 200 milliseconds for most requests. Database queries are well-optimized with proper indexes. The ALB adds approximately 5-10 milliseconds of latency, which is negligible.

**Auto-Scaling Behavior:**

During normal business hours with minimal traffic, services run at 1 task each with CPU utilization around 25-35%. I generated artificial load using Apache Bench to simulate 50 concurrent users making 1,000 requests. CPU spiked to 75%, triggering auto-scaling. Within 60 seconds, a second task started and began accepting traffic. CPU dropped back to 40% across both tasks.

After the load test ended, CPU decreased to 15% across two tasks. After the 300-second scale-in cooldown, one task was terminated, returning to the baseline of 1 task.

The scheduled scaling worked perfectly. At 11 PM EST, even though CPU was low, the scheduled action forced the maximum to 1, preventing any scale-out. At 6 AM EST, the maximum was restored to 4, allowing normal auto-scaling behavior.

**Availability:**

Multi-AZ deployment proved its worth. During an AWS maintenance event that impacted one availability zone, RDS automatically failed over to the standby instance in the other availability zone. Downtime was approximately 90 seconds, and the application recovered without intervention.

ECS tasks spread across both availability zones ensured that even if one zone experienced issues, the other zone's tasks continued serving traffic.

**Deployment Experience:**

Zero-downtime deployments work as advertised. During a deployment, the ALB continues routing traffic to old tasks while new tasks start and pass health checks. Only after new tasks are healthy does the ALB begin routing traffic to them, and old tasks are drained and terminated. Users never notice the deployment.

The average deployment time from pushing code to GitHub to new tasks running in production is approximately 5 minutes. This includes the GitHub Actions build time (2-3 minutes), ECR push time (30-60 seconds), task definition registration (instant), and ECS service update time (1-2 minutes for rolling deployment).

## Security Considerations

Security was built into every layer of the architecture.

**Network Security:**

The VPC isolates all resources from other AWS customers. Public subnets only contain the ALB. Application containers and the database reside in private subnets with no direct internet access. The NAT Gateway allows outbound connections but prevents inbound connections.

Security groups use a whitelist approach. Nothing is allowed by default. The ALB security group allows inbound HTTPS from anywhere but only because it is internet-facing. The ECS security group only allows connections from the ALB. The database security group only allows PostgreSQL connections from ECS tasks.

**Data Security:**

All data in transit uses TLS/SSL encryption. The SSL certificate from AWS Certificate Manager ensures encrypted communication between users and the ALB. Connections from the ALB to backend services use HTTP internally, which is acceptable because they never leave the VPC.

Database connections use SSL (enforced by the sslmode=require parameter in the connection string). All data at rest in RDS is encrypted using AWS KMS.

**Application Security:**

The Flask backend implements JWT-based authentication. Passwords are hashed using bcrypt before storage. SQL queries use parameterized statements through SQLAlchemy, preventing SQL injection.

CORS is configured to only allow requests from the production domain, preventing unauthorized cross-origin requests.

Rate limiting would be a valuable addition to prevent abuse, though it has not been implemented yet.

**Access Control:**

IAM follows the principle of least privilege. The GitHub Actions user has exactly the permissions needed for deployments, nothing more. The ECS task execution role has permissions to pull images from ECR and write logs to CloudWatch. The ECS task role (currently not used) would grant application containers permissions to access other AWS services if needed.

MFA is enabled on the root account and administrative IAM users, adding an extra layer of protection against credential compromise.

**Secrets Management:**

Application secrets are stored in GitHub Secrets with encryption at rest. The DATABASE_URL, SECRET_KEY, and JWT_SECRET_KEY are never committed to the repository or exposed in logs.

Future improvements would include using AWS Secrets Manager with automatic rotation, eliminating the need to store secrets in GitHub.

## The Final Result

After 11 phases spanning three weeks, the result is a production-ready application with the following characteristics:

**Availability:** The application runs 24/7 with 99.9% uptime, measured over the past month. The only downtime was the planned RDS failover during AWS maintenance.

**Scalability:** The system automatically scales from 1 task to 4 tasks per service based on demand, providing 4x capacity during peak load while minimizing costs during idle periods.

**Security:** Defense in depth with multiple security layers, encryption in transit and at rest, and least-privilege access controls.

**Observability:** Comprehensive monitoring with CloudWatch metrics, logs, and alarms providing visibility into system health and performance.

**Automation:** Zero-touch deployments from code push to production in under 5 minutes with zero downtime.

**Cost Efficiency:** Optimized infrastructure running at approximately $92 per month with further savings during low-traffic periods.

**Reliability:** Multi-AZ deployment ensures high availability even during infrastructure failures.

The application is live at https://app.techveesolutions.com and has served thousands of requests without issues.

## What is Next

This project focused on AWS deployment. The natural next step is deploying the same application to Microsoft Azure and Google Cloud Platform to compare:

**Cost differences:** How do equivalent services compare in pricing across providers?

**Feature sets:** What unique capabilities does each cloud offer?

**Developer experience:** Which platform has the best tooling and workflow?

**Performance:** Are there measurable differences in latency or throughput?

Beyond multi-cloud deployment, there are several enhancements I would like to make to this AWS deployment:

**Implement AWS WAF:** Web Application Firewall to protect against common exploits like SQL injection and cross-site scripting.

**Add CloudFront CDN:** Improve global performance by caching static assets closer to users.

**Implement container health checks:** Beyond the load balancer health checks, internal container health checks would provide better failure detection.

**Set up X-Ray tracing:** Distributed tracing to understand request flows through the system and identify bottlenecks.

**Create disaster recovery runbook:** Document and test procedures for various failure scenarios.

**Implement automated testing in CI/CD:** Add integration tests that run before deployment to catch issues earlier.

## Conclusion

Deploying a full-stack application to AWS taught me far more than any tutorial or certification course could. Every decision had tradeoffs. Every challenge had multiple solutions. Every phase built on the knowledge from previous phases.

The journey from docker-compose up to a production-ready, auto-scaling, highly-available cloud application is not trivial. But it is achievable with patience, attention to detail, and willingness to learn from mistakes.

The documentation created along the way serves as a roadmap that others can follow. Every command executed, every error encountered, and every solution implemented is recorded. This is the value of documenting as you go rather than retroactively.

For anyone considering a similar journey, my advice is simple: start small, document everything, understand the why behind each decision, do not skip security, and embrace the learning process.

The cloud is not magic. It is a collection of well-engineered services that, when combined thoughtfully, create systems that are greater than the sum of their parts. Understanding how those pieces fit together and why they are designed the way they are is the true value of this exercise.

This application is not just running in the cloud. It is running well, securely, cost-effectively, and reliably. That is the difference between deploying to production and deploying to production the right way.

---

**Project Repository:** https://github.com/vee-kay8/task-management-app
**Live Application:** https://app.techveesolutions.com
**Total Cost:** $92/month
**Deployment Time:** 3 weeks
**Lines of Documentation:** Over 15,000 words
**Phases Completed:** 11 of 12 (92% complete)

The journey continues with Phase 12 (final documentation and architecture diagrams) before moving on to Azure and GCP deployments for a comprehensive multi-cloud comparison.
