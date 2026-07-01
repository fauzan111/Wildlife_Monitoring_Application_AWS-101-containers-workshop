# Wildlife Monitoring System - User Guide

## 🌍 What Is This Application?

The **Wildlife Monitoring System** is a real-world multi-service application for rangers and wildlife researchers to:
- **Report wildlife sightings** with species, location, and image uploads
- **Track GPS-tagged animals** with collar data and battery status
- **View sightings on an interactive map** to identify hotspots and patterns
- **Manage conservation data** across a distributed architecture

## 🎯 Application Features

### 1. **Report Wildlife Sightings** (Left Panel)
- Enter species name (e.g., "African Elephant", "Lion", "Giraffe")
- Select habitat type (Forest, Grassland, Wetland, Mountain, etc.)
- Click the map to set GPS coordinates (or enter manually)
- Upload optional photos for evidence
- Track animal counts

### 2. **GPS Tracking Alerts** (Left Panel - Table)
- Real-time tracking of collared animals
- Monitor GPS collar battery levels
- Status indicators (Active, Low Battery, Offline)
- Timestamp tracking

### 3. **Interactive Map** (Right Panel - Top)
- OpenLayers-based map showing all sightings
- Click on map to set coordinates for new sightings
- View all reported wildlife locations
- Visual hotspot identification

### 4. **Recent Sightings Database** (Right Panel - Bottom)
- DataTable with all reported sightings
- Images from each sighting
- Species, habitat type, count
- Date/time tracking

## 🚀 How to Monitor Wildlife

### Step 1: Access the Application
```
Open your browser and go to:
http://wildlife-alb-ecs-1286662502.us-west-2.elb.amazonaws.com/wildlife
```

### Step 2: Report a Sighting

1. **Fill in the form** on the left side:
   - **Species**: Enter animal type (e.g., "Lion", "Zebra", "Hyena")
   - **Habitat Type**: Select from dropdown (Forest, Grassland, etc.)
   - **Latitude & Longitude**: Click map OR enter coordinates manually
   - **Number of Animals**: Enter count
   - **Image**: Upload a photo (optional)

2. **Click on the map** to set your location automatically

3. **Click "Submit Sighting"** to save the report

4. **Watch the table update** with your new sighting instantly

### Step 3: Monitor GPS-Tracked Animals

- Check the **GPS Tracking Alerts** table (left panel)
- Look for animals with:
  - **Active** status = Current signal
  - **Low Battery** = Alert needed
  - **Offline** = Lost contact
- Click on any alert to see detailed animal information

### Step 4: Analyze Patterns

- View the **Sighting Locations Map** to see:
  - Geographic distribution
  - Hotspot areas
  - Migration patterns
  - Habitat preferences

## 📊 Microservices Behind the Scenes

The application runs on 5 containerized services:

| Service | Purpose | Technology |
|---------|---------|------------|
| **Frontend** | Web UI | Flask (Python) + Bootstrap + OpenLayers |
| **DataDB** | Storage | MongoDB 8.0 with EFS persistence |
| **DataAPI** | Query API | Flask REST API |
| **Media** | Images | Flask + AWS S3 storage |
| **Alerts** | GPS Tracking | Flask + X-Ray monitoring |

### Service Communication
- **Service Connect**: Services discover each other by DNS names
  - `wildlife-app-dataapi` (internal)
  - `wildlife-app-alerts` (internal)
  - `wildlife-app-media` (internal)

## 🔍 Next Steps & Monitoring

### 1. **Monitor Application Health**
```bash
# Check if all services are running
aws ecs describe-services \
  --cluster wildlife-ecs \
  --services wildlife-datadb-service wildlife-dataapi-service \
                wildlife-alerts-service wildlife-media-service \
                wildlife-frontend-service \
  --region us-west-2 \
  --query 'services[*].[serviceName, runningCount]'
```

### 2. **View Application Logs**
```bash
# Frontend logs
aws logs tail /aws/ecs/wildlife-frontend --follow

# DataAPI logs
aws logs tail /aws/ecs/wildlife-dataapi --follow

# Alerts service logs
aws logs tail /aws/ecs/wildlife-alerts --follow
```

### 3. **Check Auto-Scaling Activity**
```bash
# Frontend scaling (target CPU 100%)
aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/wildlife-ecs/wildlife-frontend-service

# Media scaling (target CPU 30%)
aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/wildlife-ecs/wildlife-media-service
```

### 4. **Monitor with AWS X-Ray**
The application has X-Ray integration:
```bash
# View service map and traces in AWS Console:
# https://console.aws.amazon.com/xray/home?region=us-west-2#/service-map
```

### 5. **Test the Services**

#### Test Frontend Health
```bash
curl http://wildlife-alb-ecs-1286662502.us-west-2.elb.amazonaws.com/wildlife/health
```

#### Test DataAPI
```bash
curl -X POST http://wildlife-dataapi:5000/api/sightings \
  -H "Content-Type: application/json" \
  -d '{"species": "Lion", "count": 2, "latitude": -1.5, "longitude": 35.2}'
```

#### Test GPS Alerts
```bash
curl http://wildlife-alerts:5000/api/gps-data
```

## 📈 Performance Monitoring

### Key Metrics to Watch

1. **Task Count**
   - Frontend: 2 tasks (scales up to 2)
   - DataAPI: 2 tasks (stable)
   - Media: 2 tasks (scales up to 6 on high CPU)
   - DataDB: 1 task (never scales)
   - Alerts: 2 tasks (stable)

2. **Auto-Scaling Triggers**
   - **Frontend**: CPU > 100% → scales (but capped at 2)
   - **Media**: CPU > 30% → scales (2-6 tasks)

3. **Response Times**
   - API calls use Service Connect (milliseconds)
   - Database queries cached where possible
   - Images stored in S3 (fast for downloads)

## 🛠️ Common Tasks

### Add More Sightings
1. Go to the form on the left
2. Fill in details
3. Click map to set location
4. Upload photo
5. Submit

### Export Data
Data is stored in MongoDB. Query via API:
```bash
curl http://wildlife-alb-ecs-1286662502.us-west-2.elb.amazonaws.com/wildlife/api/sightings
```

### Scale Services Manually
```bash
aws ecs update-service \
  --cluster wildlife-ecs \
  --service wildlife-frontend-service \
  --desired-count 3 \
  --region us-west-2
```

### View Database
```bash
# SSH into MongoDB container
aws ecs execute-command \
  --cluster wildlife-ecs \
  --task-definition wildlife-datadb-task \
  --container wildlife-datadb \
  --interactive \
  --command "/bin/bash"
```

## 🔐 Security Features

✅ **Non-root container execution** - All services run as unprivileged user
✅ **VPC isolation** - All traffic within private subnets
✅ **Service discovery** - No public inter-service communication
✅ **Data encryption** - S3 with KMS, EFS encryption enabled
✅ **X-Ray monitoring** - Full distributed tracing
✅ **Automatic image scanning** - ECR scans for vulnerabilities

## 📝 Tips for Effective Monitoring

1. **Regular Sighting Reports**: Enter sightings as they happen
2. **Consistent Coordinates**: Use the map click feature for accuracy
3. **Photo Documentation**: Always upload if possible for verification
4. **GPS Collar Maintenance**: Monitor battery levels in GPS table
5. **Data Review**: Check Recent Sightings table for patterns
6. **Alerts**: Set up CloudWatch alarms for low battery or offline status

## 🆘 Troubleshooting

### Application Not Loading
```bash
# Check if frontend is running
aws ecs describe-services --cluster wildlife-ecs --services wildlife-frontend-service --region us-west-2
```

### Slow Performance
- Check auto-scaling metrics
- Review CloudWatch logs for errors
- Verify database connectivity
- Check S3 upload speeds

### Missing Sightings Data
- Verify MongoDB is running (wildlife-datadb-service)
- Check DataAPI logs for connection errors
- Ensure network connectivity between services

## 📞 Support

For logs and debugging:
```bash
# All service logs
aws logs tail /aws/ecs/ --follow

# X-Ray traces
# Console: AWS X-Ray → Service Map

# CloudWatch metrics
# Console: CloudWatch → Dashboards
```

---

**Happy Wildlife Monitoring! 🦁🐘🦓**
