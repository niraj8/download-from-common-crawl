resource "aws_s3_bucket" "bucket" {
  bucket = "${terraform.workspace}-common-crawl-query-${random_pet.one.id}-${random_pet.two.id}"

  tags = {
    environment = terraform.workspace
  }
}


output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value = aws_s3_bucket.bucket.id
}
