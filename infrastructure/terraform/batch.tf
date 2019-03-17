resource "aws_batch_job_definition" "feature_extractor" {
  name = "${var.system_code}-extractor-job-definition"
  type = "container"

  timeout {
    attempt_duration_seconds = 3600
  }

  container_properties = <<CONTAINER_PROPERTIES
{
  "command": ["python", "app.py"],
  "jobRoleArn": "${aws_iam_role.extractor_role.arn}",
  "image": "${var.aws_account_id}.dkr.ecr.${var.region}.amazonaws.com/${aws_ecr_repository.spot-rec-ecr.name}",
  "memory": 8192,
  "vcpus": 2,
  "volumes": [],
  "environment": [
    {
      "name": "DYNAMODB_TABLE",
      "value": "${aws_dynamodb_table.metadata_table.name}"
    },
    {
      "name": "ZIP_FILE_NAME",
      "value": ""
    },
    {
      "name": "S3_BUCKET_NAME",
      "value": "${aws_s3_bucket.audio-upload-bucket.bucket}"
    }
  ],
  "mount_points": [],
  "ulimits": []
}
CONTAINER_PROPERTIES
}

resource "aws_batch_compute_environment" "extractor_environment" {
  compute_environment_name = "${var.system_code}-environment"

  compute_resources {
    instance_role = "${aws_iam_instance_profile.ecs_instance_role.arn}"

    instance_type = [
      "optimal",
    ]

    max_vcpus     = 16
    desired_vcpus = 4
    min_vcpus     = 0

    security_group_ids = [
      "${var.security_group}",
    ]

    subnets = [
      "${var.subnet_id}",
    ]

    type = "EC2"
  }

  service_role = "${aws_iam_role.aws_batch_service_role.arn}"
  type         = "MANAGED"
  depends_on   = ["aws_iam_role_policy_attachment.aws_batch_service_role"]
}

resource "aws_batch_job_queue" "extractor_queue" {
  name     = "${var.system_code}-job-queue"
  state    = "ENABLED"
  priority = 1

  compute_environments = [
    "${aws_batch_compute_environment.extractor_environment.arn}",
  ]
}
