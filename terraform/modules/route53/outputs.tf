output "record_name" {
  description = "Name of the Route53 record"
  value       = aws_route53_record.app.name
}

output "record_fqdn" {
  description = "FQDN of the Route53 record"
  value       = aws_route53_record.app.fqdn
}
