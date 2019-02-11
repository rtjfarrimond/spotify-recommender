data "aws_ecs_task_definition" "extractor" {
  task_definition = "${aws_ecs_task_definition.extractor.family}"
}

resource "aws_ecr_repository" "spot-rec-ecr" {
  name = "${var.system_code}-${var.extractor_image}"
}

resource "aws_ecs_cluster" "spot-rec-ecs-cluster" {
  name = "${var.system_code}-ecs-cluster"
}

resource "aws_ecs_task_definition" "extractor" {
  family = "${var.system_code}"

  container_definitions = <<DEFINITION
[
  {
    "cpu": 128,
    "environment": [{
      "name": "SECRET",
      "value": "KEY"
    }],
    "essential": true,
    "image": "${aws_ecr_repository.spot-rec-ecr.repository_url}",
    "memory": 128,
    "memoryReservation": 64,
    "name": "${var.extractor_image}"
  }
]
DEFINITON
}

resource "aws_ecs_service" "extractor-service" {
  name = "${var.extractor_image}-service"
  cluster = "${aws_ecs_cluster.spot-rec-ecs-cluster.id}"
  desired_count = 0
  launch_type = "FARGATE"

  task_definition = "${aws_ecs_task_definition.extractor.family}:${max("${aws_ecs_task_definition.extractor.revision}", "${data.aws_ecs_task_definition.extractor.revision}")}"
}

output "ecr_repo_uri" {
  value = "${aws_ecr_repository.spot-rec-ecr.repository_url}"
}
