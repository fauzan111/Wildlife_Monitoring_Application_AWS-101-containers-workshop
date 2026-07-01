# Wildlife Monitoring System - Operations & Monitoring Guide

## 🎛️ Monitoring & Management

### Real-Time Monitoring Commands

#### 1. Check All Services Status
```bash
aws ecs describe-services \
  --cluster wildlife-ecs \
  --services wildlife-frontend-service wildlife-datadb-service \
                wildlife-dataapi-service wildlife-alerts-service \
                wildlife-media-service \
  --region us-west-2 \
  --query 'services[*].[serviceName, runningCount, desiredCount, status]' \
  --output table
```

#### 2. Monitor Tasks Running
```bash
# List all running tasks
aws ecs list-tasks \
  --cluster wildlife-ecs \
  --region us-west-2 \
  --output text | tr '\t' '\n'

# Get detailed task info
aws ecs describe-tasks \
  --cluster wildlife-ecs \
  --tasks <task-arn> \
  --region us-west-2 \
  --query 'tasks[*].[taskArn, lastStatus, cpuUtilization, memoryUtilization]'
```

#### 3. View Service Events
```bash
aws ecs describe-services \
  --cluster wildlife-ecs \
  --services wildlife-frontend-service \
  --region us-west-2 \
  --query 'services[0].events[:10]' \
  --output text
```

### 📊 CloudWatch Monitoring

#### View Logs for Each Service
```bash
# Frontend
aws logs tail /aws/ecs/wildlife-frontend --follow --since 1h

# Data API
aws logs tail /aws/ecs/wildlife-dataapi --follow --since 1h

# Alerts Service
aws logs tail /aws/ecs/wildlife-alerts --follow --since 1h

# Media Service
aws logs tail /aws/ecs/wildlife-media --follow --since 1h

# MongoDB
aws logs tail /aws/ecs/wildlife-datadb --follow --since 1h
```

#### Search Logs for Errors
```bash
aws logs filter-log-events \
  --log-group-name /aws/ecs/wildlife-frontend \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --end-time $(date +%s)000
```

### 🔄 Auto-Scaling Management

#### Check Auto-Scaling Configuration
```bash
# Frontend scaling target
aws application-autoscaling describe-scalable-targets \
  --service-namespace ecs \
  --resource-ids service/wildlife-ecs/wildlife-frontend-service

# Media scaling target
aws application-autoscaling describe-scalable-targets \
  --service-namespace ecs \
  --resource-ids service/wildlife-ecs/wildlife-media-service
```

#### Check Recent Scaling Activity
```bash
# Frontend scaling events
aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/wildlife-ecs/wildlife-frontend-service \
  --max-results 10

# Media scaling events
aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/wildlife-ecs/wildlife-media-service \
  --max-results 10
```

### 🛠️ Manual Service Management

#### Scale a Service Up
```bash
aws ecs update-service \
  --cluster wildlife-ecs \
  --service wildlife-frontend-service \
  --desired-count 4 \
  --region us-west-2
```

#### Scale a Service Down
```bash
aws ecs update-service \
  --cluster wildlife-ecs \
  --service wildlife-media-service \
  --desired-count 2 \
  --region us-west-2
```

#### Force Service Update (Deploy New Version)
```bash
aws ecs update-service \
  --cluster wildlife-ecs \
  --service wildlife-frontend-service \
  --force-new-deployment \
  --region us-west-2
```

#### Stop All Tasks in a Service
```bash
aws ecs update-service \
  --cluster wildlife-ecs \
  --service wildlife-alerts-service \
  --desired-count 0 \
  --region us-west-2
```

### 🔍 Debugging & Troubleshooting

#### Execute Command in Container
```bash
# SSH into running container
aws ecs execute-command \
  --cluster wildlife-ecs \
  --task <task-id> \
  --container wildlife-frontend \
  --interactive \
  --command "/bin/sh"
```

#### View Container Logs
```bash
# Through CloudWatch Logs
aws logs get-log-events \
  --log-group-name /aws/ecs/wildlife-frontend \
  --log-stream-name <stream-name>
```

#### Stop and Restart a Task
```bash
# Stop a specific task
aws ecs stop-task \
  --cluster wildlife-ecs \
  --task <task-arn> \
  --reason "Manual restart" \
  --region us-west-2

# ECS will automatically start a new one due to desired_count=2
```

### 📈 Performance Metrics

#### Get CPU and Memory Usage
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value=wildlife-ecs \
                Name=ServiceName,Value=wildlife-frontend-service \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

#### Monitor Network Throughput
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name NetworkIn \
  --dimensions Name=ClusterName,Value=wildlife-ecs \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### 🔐 Security Monitoring

#### Check Image Scanning Results
```bash
aws ecr describe-image-scan-findings \
  --repository-name wildlife/frontend \
  --image-id imageTag=latest \
  --region us-west-2
```

#### List Image Vulnerabilities
```bash
for repo in wildlife/frontend wildlife/dataapi wildlife/alerts wildlife/media wildlife/datadb; do
  echo "Checking $repo..."
  aws ecr describe-images \
    --repository-name $repo \
    --region us-west-2 \
    --query 'imageDetails[0].imageScanFindingsSummary'
done
```

### 📡 Network & Service Discovery

#### Test Service Connectivity
```bash
# From within a container, test inter-service communication:
curl http://wildlife-dataapi:5000/health
curl http://wildlife-alerts:5000/health
curl http://wildlife-media:5000/health
```

#### Check Service Discovery Records
```bash
aws servicediscovery discover-instances \
  --namespace-name wildlife-app \
  --service-name frontend \
  --region us-west-2
```

### 🗄️ Database Monitoring

#### Check MongoDB Disk Usage
```bash
# Connect to MongoDB container
aws ecs execute-command \
  --cluster wildlife-ecs \
  --task <datadb-task-id> \
  --container wildlife-datadb \
  --interactive \
  --command "mongo admin --eval 'db.stats()'"
```

#### Monitor EFS Storage
```bash
aws efs describe-file-systems \
  --query 'FileSystems[?Name==`wildlife-efs`]' \
  --region us-west-2
```

### 📹 X-Ray Tracing

#### View Service Map
```bash
# Generates service map showing all service interactions
# Open in console: https://console.aws.amazon.com/xray/home?region=us-west-2#/service-map
```

#### Get X-Ray Traces
```bash
aws xray get-trace-summaries \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --region us-west-2
```

## 📊 Creating CloudWatch Dashboard

```bash
# Create dashboard with key metrics
aws cloudwatch put-dashboard \
  --dashboard-name wildlife-monitoring \
  --dashboard-body file://dashboard-config.json
```

Example dashboard-config.json:
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [ "AWS/ECS", "CPUUtilization", { "stat": "Average" } ],
          [ ".", "MemoryUtilization", { "stat": "Average" } ]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-west-2",
        "title": "Wildlife Services - CPU & Memory"
      }
    }
  ]
}
```

## 🚨 Setting Up Alarms

### Alert on High CPU
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name wildlife-frontend-high-cpu \
  --alarm-description "Frontend CPU above 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-west-2:489619622105:alerts
```

### Alert on Task Failures
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name wildlife-datadb-task-failures \
  --alarm-description "DataDB task failures detected" \
  --metric-name TaskFailures \
  --namespace AWS/ECS \
  --statistic Sum \
  --period 60 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1
```

## 🔄 Updating Services

### Deploy New Frontend Image
```bash
# 1. Build new image
cd /home/ec2-user/workspace/my-workspace/container-app/frontend
docker build -t 489619622105.dkr.ecr.us-west-2.amazonaws.com/wildlife/frontend:v2 .

# 2. Push to ECR
docker push 489619622105.dkr.ecr.us-west-2.amazonaws.com/wildlife/frontend:v2

# 3. Update task definition with new image tag
aws ecs register-task-definition \
  --family wildlife-frontend-task \
  --container-definitions '[{"name":"wildlife-frontend","image":"489619622105.dkr.ecr.us-west-2.amazonaws.com/wildlife/frontend:v2"}]'

# 4. Update service with new task definition
aws ecs update-service \
  --cluster wildlife-ecs \
  --service wildlife-frontend-service \
  --task-definition wildlife-frontend-task:2 \
  --force-new-deployment
```

## 📋 Maintenance Checklist

- [ ] Check CloudWatch logs daily
- [ ] Monitor auto-scaling activity
- [ ] Verify all services are running
- [ ] Check ECR image scan results
- [ ] Review X-Ray service map for bottlenecks
- [ ] Monitor disk usage on EFS
- [ ] Backup MongoDB data
- [ ] Clean up old images in ECR
- [ ] Review security group rules
- [ ] Update Docker base images

---

For more information, see the main Wildlife Monitoring Guide at:
`/home/ec2-user/workspace/my-workspace/WILDLIFE_MONITORING_GUIDE.md`
