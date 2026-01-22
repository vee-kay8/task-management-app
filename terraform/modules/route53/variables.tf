variable "domain_name" {
  description = "Domain name for the Route53 hosted zone"
  type        = string
}

variable "subdomain" {
  description = "Subdomain for the application"
  type        = string
}

variable "alb_dns_name" {
  description = "DNS name of the ALB"
  type        = string
}

variable "alb_zone_id" {
  description = "Zone ID of the ALB"
  type        = string
}
