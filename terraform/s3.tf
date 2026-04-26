# S3 Bucket for Music Recommendation Data
resource "aws_s3_bucket" "music_data" {
  bucket = "music-recommendation-data-${var.environment}"

  tags = {
    Name        = "Music Recommendation Data"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "music_data" {
  bucket = aws_s3_bucket.music_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "music_data" {
  bucket = aws_s3_bucket.music_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "music_data" {
  bucket = aws_s3_bucket.music_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Upload initial data file
resource "aws_s3_object" "songs_data" {
  bucket = aws_s3_bucket.music_data.id
  key    = "songs_500_final.csv"
  source = "../data/songs_500_final.csv"
  etag   = filemd5("../data/songs_500_final.csv")

  tags = {
    Name = "Songs Dataset"
  }
}