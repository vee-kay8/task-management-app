module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  vpc_cidr     = "10.0.0.0/16"
}

module "security" {
  source = "./modules/security"

  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
}

module "rds" {
  source = "./modules/rds"

  project_name          = var.project_name
  private_subnet_ids    = module.vpc.private_subnet_ids
  rds_security_group_id = module.security.rds_security_group_id
  db_password           = var.db_password
}

module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
}

module "ecs" {
  source       = "./modules/ecs"
  project_name = var.project_name
  aws_region   = var.aws_region

  private_subnet_ids         = module.vpc.private_subnet_ids
  backend_security_group_id  = module.security.backend_security_group_id
  backend_target_group_arn   = module.alb.backend_target_group_arn
  frontend_target_group_arn  = module.alb.frontend_target_group_arn
  
  execution_role_arn = "arn:aws:iam::858448674350:role/ecsTaskExecutionRole"
  backend_image_url  = module.ecr.backend_repository_url
  frontend_image_url = module.ecr.frontend_repository_url
  
  database_url    = "postgresql://postgres:${var.db_password}@${module.rds.db_endpoint}/taskmanagement"
  secret_key      = var.secret_key
  jwt_secret_key  = var.jwt_secret_key
  api_url         = "http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com"
}

module "alb" {
  source                 = "./modules/alb"
  project_name           = var.project_name
  vpc_id                 = module.vpc.vpc_id
  public_subnet_ids      = module.vpc.public_subnet_ids
  alb_security_group_id  = module.security.alb_security_group_id
  certificate_arn        = "arn:aws:acm:us-east-1:858448674350:certificate/095aa45c-e956-4590-b384-22eea11e5185"
}

module "route53" {
  source       = "./modules/route53"
  domain_name  = "techveesolutions.com"
  subdomain    = "app.techveesolutions.com"
  alb_dns_name = module.alb.alb_dns_name
  alb_zone_id  = module.alb.alb_zone_id
}
