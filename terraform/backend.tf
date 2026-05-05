terraform {
  backend "s3" {
    bucket         = "music-recommendation-terraform-state"  # Will be created manually first
    key            = "terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}