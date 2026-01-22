terraform {
  backend "s3" {
    bucket         = "taskapp-terraform-state-858448674350"  # Replace with your account ID
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "taskapp-terraform-locks"
  }
}