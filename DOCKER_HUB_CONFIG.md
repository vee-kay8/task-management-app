# Docker Hub Configuration

## Image Naming Convention
```
<docker-hub-username>/task-management-backend:<version>
<docker-hub-username>/task-management-frontend:<version>
```

## Semantic Versioning Strategy
- **Format**: MAJOR.MINOR.PATCH (e.g., 1.0.0)
- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.0.0 → 1.1.0)
- **PATCH**: Bug fixes, backward compatible (e.g., 1.0.0 → 1.0.1)

## Tags Strategy
Each image will have multiple tags:
1. **Specific version**: `1.0.0` (pinned version)
2. **Minor version**: `1.0` (latest patch of 1.0.x)
3. **Major version**: `1` (latest minor of 1.x.x)
4. **Latest**: `latest` (most recent stable release)

## Current Version
**v1.0.0** - Initial production release

## Instructions

### Setup (One-time)
Replace `<docker-hub-username>` with your actual Docker Hub username in this document.

### Tag and Push Images
```bash
# Set your Docker Hub username
export DOCKER_USERNAME=your-username-here
export VERSION=1.0.0

# Tag backend images
docker tag task-management-backend:latest $DOCKER_USERNAME/task-management-backend:$VERSION
docker tag task-management-backend:latest $DOCKER_USERNAME/task-management-backend:1.0
docker tag task-management-backend:latest $DOCKER_USERNAME/task-management-backend:1
docker tag task-management-backend:latest $DOCKER_USERNAME/task-management-backend:latest

# Tag frontend images
docker tag task-management-frontend:latest $DOCKER_USERNAME/task-management-frontend:$VERSION
docker tag task-management-frontend:latest $DOCKER_USERNAME/task-management-frontend:1.0
docker tag task-management-frontend:latest $DOCKER_USERNAME/task-management-frontend:1
docker tag task-management-frontend:latest $DOCKER_USERNAME/task-management-frontend:latest

# Push all tags to Docker Hub
docker push $DOCKER_USERNAME/task-management-backend:$VERSION
docker push $DOCKER_USERNAME/task-management-backend:1.0
docker push $DOCKER_USERNAME/task-management-backend:1
docker push $DOCKER_USERNAME/task-management-backend:latest

docker push $DOCKER_USERNAME/task-management-frontend:$VERSION
docker push $DOCKER_USERNAME/task-management-frontend:1.0
docker push $DOCKER_USERNAME/task-management-frontend:1
docker push $DOCKER_USERNAME/task-management-frontend:latest
```

### Pull Images
```bash
# Pull specific version (recommended for production)
docker pull $DOCKER_USERNAME/task-management-backend:1.0.0
docker pull $DOCKER_USERNAME/task-management-frontend:1.0.0

# Pull latest (for development)
docker pull $DOCKER_USERNAME/task-management-backend:latest
docker pull $DOCKER_USERNAME/task-management-frontend:latest
```

### Version Update Workflow
```bash
# 1. Update VERSION file
echo "1.0.1" > VERSION

# 2. Rebuild images
docker-compose build

# 3. Tag new version
export VERSION=$(cat VERSION)
# ... repeat tagging process with new version

# 4. Push to Docker Hub
# ... repeat push process

# 5. Update docker-compose.yml image references
```

## Repository URLs
After pushing, images will be available at:
- Backend: `https://hub.docker.com/r/<docker-hub-username>/task-management-backend`
- Frontend: `https://hub.docker.com/r/<docker-hub-username>/task-management-frontend`
