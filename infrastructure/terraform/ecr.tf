resource "aws_ecr_repository" "spot-rec-ecr" {
  name = "${var.system_code}-${var.extractor_image}"
}

output "ecr_repo_uri" {
  value = "${aws_ecr_repository.spot-rec-ecr.repository_url}"
}

