resource "aws_ecr_repository" "spot-rec-ecr" {
  name = "${var.system_code}-${var.extractor_image}"
}

resource "aws_ecs_cluster" "spot-rec-ecs-cluster" {
  name = "${var.system_code}-ecs-cluster"
}

output "ecr_repo_uri" {
  value = "${aws_ecr_repository.spot-rec-ecr.repository_url}"
}
