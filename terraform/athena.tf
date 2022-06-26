resource "aws_athena_database" "athena_database" {
  name   = "${terraform.workspace}_common_crawl_query_${random_pet.underscore.id}"
  bucket = aws_s3_bucket.bucket.id
}

resource "aws_athena_workgroup" "athena_workgroup" {
  name = "${terraform.workspace}_common_crawl_query_${random_pet.underscore.id}"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.bucket.id}/output/"
    }
  }
}

resource "null_resource" "views" {
    provisioner     "local-exec" {
        command = <<EOF
        aws athena start-query-execution \
        --region ${var.aws_region} \
        --output json \
        --query-string file://create_ccindex.athena \
        --query-execution-context "Database=${aws_athena_database.athena_database.name}" \
        --work-group ${aws_athena_workgroup.athena_workgroup.id}
EOF
    }
}